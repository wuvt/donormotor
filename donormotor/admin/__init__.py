from flask import Blueprint

bp = Blueprint('admin', __name__)

from donormotor.admin import views
from donormotor.admin import view_utils
