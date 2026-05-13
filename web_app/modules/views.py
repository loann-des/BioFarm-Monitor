import logging as lg
import pandas as pd

from datetime import datetime
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user, AnonymousUserMixin # type: ignore
from io import BytesIO

from web_app.models.pharmacie import PharmacieUtils

from web_app.connnected_user_web.connected_user import ConnectedUser

from web_app.fonction import *
from web_app.models.cow import CowUtils
from web_app.models.user import UserUtils

views = Blueprint('views', __name__)

# TODO Metre en place les log
# TODO Metre en place historique commande pour retour
# TODO gestion de la reintroduction d'une vache


current_user : ConnectedUser

@views.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for('auth.logout'))

@login_required
@views.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html")


@login_required
@views.route("/herd", methods=["GET"])
def herd():
    return render_template("herd.html")


@login_required
@views.route("/reproduction", methods=["GET"])
def reproduction():
    return render_template("reproduction.html")


@login_required
@views.route("/medicine_cabinet", methods=["GET"])
def pharmacie():
    return render_template("medicine-cabinet.html")


@login_required
@views.route("/settings", methods=["GET"])
def settings():
    message_dry_time : str = str(current_user.setting["dry_time"] or 'Durée_de_tarissement_en_jours') 
    message_calving_preparation = str(current_user.setting["calving_preparation_time"] or 'Durée_de_préparation_en_jours')
    return render_template("settings.html",
                           dry_time=message_dry_time,
                           calving_preparation=message_calving_preparation)
