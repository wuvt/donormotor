from flask import current_app, render_template
from donormotor import redis_conn
from email.mime.text import MIMEText
import email.utils
import smtplib


def send_receipt(order):
    try:
        ack_email_body = redis_conn.get('ack_email').decode()
    except:
        ack_email_body = ''
    msg = MIMEText(render_template('donate/email/receipt.txt',
                                   order=order, ack_email_body=ack_email_body))
    msg['Date'] = email.utils.formatdate()
    msg['From'] = current_app.config['DONATE_MAIL_FROM']
    msg['To'] = order.email
    msg['Message-Id'] = email.utils.make_msgid()
    msg['X-Mailer'] = "wuvt-site"
    msg['Subject'] = "Thanks from {0}".format(
        current_app.config['STATION_NAME'])

    try:
        s = smtplib.SMTP(current_app.config['SMTP_SERVER'])
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
    except Exception as exc:
        current_app.logger.warning(
            "Donate: Failed to email receipt for order {0}: {1}".format(
                order.id, exc))
