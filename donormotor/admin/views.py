import boto3
import datetime
import dateutil.parser
import os
from flask import abort, flash, jsonify, make_response, render_template, \
        redirect, request, url_for
from werkzeug import secure_filename

from donormotor import app, auth_manager, cache, db, redis_conn
from donormotor.auth import current_user, login_required
from donormotor.admin import bp
from donormotor.auth.models import User
from donormotor.admin.auth import views as auth_views  # noqa: F401
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
    if not app.config['DONATE_ENABLE']:
        abort(404)

    if request.method == 'POST':
        if 'reset_stats' in request.form:
            redis_conn.set('donation_stats_start',
                           datetime.datetime.utcnow().isoformat())
        return redirect(url_for('.donation_index'))

    stats = Order.query.with_entities(
        db.func.sum(Order.amount).label('total_paid'),
        db.func.max(Order.amount).label('max_paid'))

    donation_stats_start = redis_conn.get('donation_stats_start')
    if donation_stats_start is not None:
        last_stats_reset = dateutil.parser.parse(donation_stats_start)
        stats = stats.filter(Order.placed_date > last_stats_reset)
    else:
        last_stats_reset = None

    stats = stats.all()

    total = stats[0][0]
    if total is None:
        total = 0

    max_donation = stats[0][1]
    if max_donation is None:
        max_donation = 0

    donations = Order.query.all()

    return render_template('admin/donation_index.html',
                           donations=donations,
                           total=total,
                           max=max_donation,
                           last_stats_reset=last_stats_reset)

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

@bp.route('/premium-config')
@auth_manager.check_access('business')
def premium_config():
    #TODO add form handling for this, store config in redis?
    return render_template('admin/premium_config')
