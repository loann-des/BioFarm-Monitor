import json
import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    render_template,
    url_for
)

from flask_login import login_required, current_user

from web_app.fonction import parse_date # type: ignore

from ..connnected_user_web.connected_user import ConnectedUser
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

@login_required
@cowbp.route("/cow/change", methods=["POST"])
def change():
    try:
        cow_id = int(request.form["cow_id"])

        if request.form["name"]:
            CowUtils.update_cow(current_user.id, cow_id,
                name=request.form["name"])

        if request.form["birthdate"]:
            CowUtils.update_cow(current_user.id, cow_id,
                born_date = parse_date(request.form["birthdate"]))

        return jsonify({
            "success": True,
            "message": f"Vache {cow_id} modifiée"
        })
    except Exception as e:
        lg.error(f"Erreur lors de la modification de la vache: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de la modification de la vache: {e}"
        })

@login_required
@cowbp.route("/cow/add-insemination", methods=["POST"])
def add_insemination():
    try:
        cow_id = int(request.form["cow_id"])
        inseminsation_date = request.form["date"]

        if inseminsation_date:
            CowUtils.add_insemination(current_user.id, cow_id, inseminsation_date)

            return jsonify({
                "success": True,
                "message": f"Insémination ajoutée à la vache {cow_id} pour " +
                    f"l'utilisateur {current_user.id}"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Date manquante pour l'insémination"
            })
    except Exception as e:
        lg.error(f"Erreur lors de l'ajout de la reproduction: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de l'ajout de la reproduction: {e}"
        })

@login_required
@cowbp.route("/cow/get-inseminations", methods=["GET"])
def get_inseminations():
    if request.args.get("cow_id") is None:
        return jsonify({
            "success": False,
            "message": "Argument cow_id is missing"
        })

    try:
        cow_id = int(request.args.get("cow_id"))

        cow = CowUtils.get_cow(current_user.id, cow_id)

        return jsonify({
            "success": True,
            "message": cow.reproduction
        })
    except Exception as e:
        lg.error(f"Failed to get cow reproductions: {e}")

        return jsonify({
            "success": False,
            "message": f"Failed to get cow reproductions: {e}"
        })
