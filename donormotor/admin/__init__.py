from flask import Blueprint

bp = Blueprint('admin', __name__)

from donormotor.admin import views
