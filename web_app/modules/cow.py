import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    render_template,
    url_for
)

from flask_login import login_required, current_user # type: ignore

from ..connected_user import ConnectedUser
from web_app.models.cow import CowUtils

cowbp = Blueprint("cow", __name__)

current_user: ConnectedUser

@cowbp.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))

@login_required
@cowbp.route("/cow/<int:cow_id>", methods=["GET"])
def display_cow(cow_id):
    cow = CowUtils.get_cow(current_user.id, cow_id)

    return render_template("cow.html", cow=cow)

@login_required
@cowbp.route("/cow/remove", methods=["POST"])
def remove_cow():
    cow_id = int(request.form["id"])
    user_id = current_user.id

    try:
        CowUtils.remove_cow(user_id, cow_id)

        return jsonify({
            "success": True,
            "message": f"La sortie de la vache {cow_id} a bien été enregistrée"
        })
    except Exception as e:
        lg.error(f"Erreur lors de la sortie de la vache {cow_id}: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de la sortie de la vache {cow_id}"
        })
