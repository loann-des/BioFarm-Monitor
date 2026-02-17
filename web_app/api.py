import logging as lg
import pandas as pd

from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user, AnonymousUserMixin # type: ignore
from io import BytesIO

from .fonction import *

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
def api_login():
    # TODO Implement API login
    return jsonify({"message": "API login not implemented yet"}), 501

@api.route('/CMD', methods=['POST'])
def api_command():
    
    # TODO Implement API command processing
    return jsonify({"message": "API command processing not implemented yet"}), 501