import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    url_for
)

from datetime import datetime
from flask_login import login_required, current_user

from ..connected_user import ConnectedUser
from ..models import CowUtils

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

    return [cow.to_json() for cow in cows]

@login_required
@herd.route("/herd/acquire", methods=["POST"])
def acquire():
    try:
        user_id = current_user.id
        # Récupération des données du formulaire
        cow_id = int(request.form["id"])

        lg.info(f"Adding new cow {cow_id}...")

        CowUtils.add_cow(user_id=user_id, cow_id=cow_id, init_as_cow=True)

        return jsonify(
            {"success": True, "message": f"{cow_id} a été ajoutée avec succès !"}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})
