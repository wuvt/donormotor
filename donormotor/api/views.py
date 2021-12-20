from flask import request, json, make_response, url_for

from donormotor import app, redis_conn
from donormotor.api import bp

@bp.route('/v1/radiothon')
def is_radiothon():
    try:
        radiothon = redis_conn.get('radiothon').decode()
    except:
        radiothon = 'false'
    return { "radiothon": radiothon }
