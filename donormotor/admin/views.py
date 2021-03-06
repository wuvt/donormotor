import boto3
import datetime
import dateutil.parser
import os
from flask import abort, flash, jsonify, make_response, render_template, \
        redirect, request, url_for, json
from werkzeug.utils import secure_filename

from donormotor import app, auth_manager, cache, redis_conn
from donormotor.admin import bp
from donormotor.admin.auth import views as auth_views  # noqa: F401
from donormotor.admin.view_utils import donation_stats
from donormotor.auth import current_user, login_required
from donormotor.auth.models import User
from donormotor.db import db
from donormotor.donate.models import Order
import csv
import io


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@bp.route('/upload', methods=['GET', 'POST'])
@auth_manager.check_access('admin', 'content')
def upload():
    if request.method == 'GET':
        return render_template('admin/upload.html')
    else:
        uploaded = request.files['file']
        destdir = secure_filename(request.form['destination'])

        if destdir == 'default':
            destdir = ''

        if uploaded:
            filename = secure_filename(uploaded.filename)
            filepath = os.path.join(destdir, filename)

            if len(app.config['UPLOAD_S3_BUCKET']) > 0:
                aws_config = {}
                if len(app.config['UPLOAD_S3_ENDPOINT']) > 0:
                    aws_config['endpoint_url'] = app.config[
                        'UPLOAD_S3_ENDPOINT']
                if len(app.config['UPLOAD_S3_REGION']) > 0:
                    aws_config['region_name'] = app.config['UPLOAD_S3_REGION']

                s3 = boto3.resource('s3', **aws_config)
                s3.meta.client.upload_fileobj(
                    uploaded,
                    app.config['UPLOAD_S3_BUCKET'],
                    filepath)
            else:
                uploaded.save(os.path.join(app.config['UPLOAD_DIR'], filepath))

            upload_url = app.config['UPLOAD_URL'] + '/' + filepath
            flash('Your file has been uploaded to: ' + upload_url)

        return render_template('admin/upload.html')

@bp.route('/donations', methods=['GET', 'POST'])
@auth_manager.check_access('business')
def donation_index():

    if request.method == 'POST':
        if 'reset_stats' in request.form:
            redis_conn.set('donation_stats_start',
                           datetime.datetime.utcnow().isoformat())
        if 'set_paid' in request.form:
            # TODO log who set as paid
            o = Order.query.get(request.form["id"])
            o.set_paid(method="check")
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

        # TODO support setting asynchronously, rather than redirecting
        if 'set_shipped' in request.form:
            # TODO log who set as paid
            o = Order.query.get(request.form["id"])
            o.set_shipped()
            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise


        return redirect(url_for('.donation_index'))

    startdate = redis_conn.get('donation_stats_start')

    stats = donation_stats(startdate)
    
    donations = Order.query.all()

    return render_template('admin/donation_index.html',
                           donations=donations,
                           total=stats['total'],
                           max=stats['max_donation'],
                           last_stats_reset=stats['last_stats_reset'])

@bp.route('/reports', methods=['GET', 'POST'])
@auth_manager.check_access('business')
def donate_reports_and_stats():

    if request.method == 'POST':
        if 'reset_stats' in request.form:
            redis_conn.set('donation_stats_start',
                           datetime.datetime.utcnow().isoformat())
        return redirect(url_for('.donate_reports_and_stats'))

    startdate = redis_conn.get('donation_stats_start')

    stats = donation_stats(startdate)

    return render_template('admin/reports.html',
                           total=stats['total'],
                           max=stats['max_donation'],
                           last_stats_reset=stats['last_stats_reset'])

@bp.route('/donate/csv')
@auth_manager.check_access('business')
def donate_csv_download():
    csvHeaders = ["id", "name", "email", "phone", "date", "address",
                  "useragent", "dj", "thanks", "firsttime", "dcomment",
                  "premiums", "address1", "address2", "city", "state", "zip",
                  "amount", "recurring", "paiddate", "shippeddate",
                  "shirtsize", "shirtcolor", "sweatshirtsize", "method",
                  "custid", "donor_comment"]
    orders = Order.query.\
        order_by(db.desc(Order.id))
    f = io.StringIO()
    writer = csv.writer(f)
    writer.writerow(csvHeaders)
    for o in orders:
        fields = [o.id, o.name, o.email, o.phone, o.placed_date, o.remote_addr,
                  o.user_agent, o.dj, o.thank_on_air, o.first_time,
                  o.donor_comment, o.premiums, o.address1, o.address2, o.city,
                  o.state, o.zipcode, o.amount, o.recurring, o.paid_date,
                  o.shipped_date, o.tshirtsize, o.tshirtcolor, o.sweatshirtsize,
                  o.method, o.custid, o.donor_comment]
        writer.writerow(fields)
    f.seek(0)
    filename = "donor-premiums.csv"
    return f.read(), {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition":
            "attachment; filename=\"{0}\"".format(filename),
    }

@bp.route('/premium-config', methods=['GET', 'POST'])
@auth_manager.check_access('business')
def premium_config():
    #TODO add form handling for this, store config in redis?
    default_premiums = b'{"enabled":true,"premiums":{"sweatshirt":{"display":"Sweatshirt","sizes":["None","S","M","L","XL","XXL"]},"tshirt":{"display":"T-Shirt","sizes":["None","S","M","L","XL","XXL"]}},"shipping_cost":600,"shipping_minimum":2000}'
    if request.method == 'GET':
        try:
            radiothon = redis_conn.get('radiothon').decode()
        except:
            radiothon = "false"
            redis_conn.set('radiothon', b"false")
        try:
            premiums = json.loads(redis_conn.get('donate_premiums_config'))
        except:
            premiums = default_premiums.decode()
            redis_conn.set('donate_premiums_config', default_premiums)
        try:
            ack_email=redis_conn.get('ack_email').decode()
        except:
            ack_email=""
        return render_template('admin/premium_config.html',
                radiothon=radiothon,
                premiums=premiums,
                ack_email=ack_email)
    if request.method == 'POST':
        if 'enable_radiothon' in request.form:
            redis_conn.set('radiothon', b"true")
        elif 'disable_radiothon' in request.form:
            redis_conn.set('radiothon', b"false")
        if 'default_premiums' in request.form:
            p = default_premiums
            redis_conn.set('donate_premiums_config', p)
        elif 'premiums' in request.form:
            p = json.dumps(request.form['premiums'])
            redis_conn.set('donate_premiums_config', p)
        if 'default_ack_email' in request.form:
            redis_conn.set('ack_email', b'');
        elif 'update_ack_email' in request.form:
            p = request.form['ack_email'].encode()
            redis_conn.set('ack_email', p)
        return redirect(url_for('.premium_config'))
