import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    url_for
)

from datetime import datetime
from flask_login import login_required, current_user # type: ignore

from web_app.connnected_user_web.connected_user import ConnectedUser
from web_app.fonction import parse_date
from web_app.models.cow import CowUtils

herd = Blueprint("herd", __name__)

current_user: ConnectedUser

@herd.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for("auth.logout"))

@login_required
@herd.route("/herd/list")
def list():
    cows = CowUtils.get_all_cows(current_user.id)

    return [cow.to_json() for cow in cows] #TODO masmalow

@login_required
@herd.route("/herd/list/filter", methods=["GET"])
def list_filter():
    idsearch = str(request.args.get("id_filter"))

    cows = filter(lambda cow: idsearch in str(cow.cow_id),
            CowUtils.get_all_cows(current_user.id))

    return [cow.to_json() for cow in cows] #TODO masmalow

@login_required
@herd.route("/herd/acquire", methods=["POST"])
def acquire():
    try:
        user_id = current_user.id
        # Récupération des données du formulaire
        cow_id = int(request.form["id"])
        cow_name = str(request.form["name"])
        birth_date = parse_date(request.form["birth_date"])

        if cow_name is None or len(cow_name) == 0:
            cow_name = "N/A"

        lg.info(f"Adding new cow {cow_id}...")

        current_user.cow_ustils.add_cow(cow_id, cow_name, birth_date, False)

        return jsonify(
            {"success": True, "message": f"{cow_id} a été ajoutée avec succès !"}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})
