from flask import Blueprint

bp = Blueprint('api', __name__)

from donormotor.api import views
