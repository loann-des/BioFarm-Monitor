# Pharmacie form
import logging as lg

from datetime import datetime
from flask import Blueprint, jsonify, redirect, request, url_for
from flask_login import login_required, current_user  # type: ignore

from web_app.fonction import (
    get_all_calving_date,
    get_all_calving_preparation_date,
    get_all_dry_date
)
from web_app.models import CowUtils, Users


repro = Blueprint('repro', __name__)

current_user : Users

# Reproduction form
@repro.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for('auth.logout'))

@login_required
@repro.route("/add_cow", methods=["POST"])
def add_cow():
    # TODO gestion veaux upload_cow
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


@login_required
@repro.route("/remove_cow", methods=["POST"])
def remove_cow():

    try:
        # Récupération des données du formulaire
        cow_id = int(request.form["id"])

        lg.info(f"supresion de {cow_id}...")

        CowUtils.remove_cow(user_id=current_user.id, cow_id=cow_id)

        return jsonify({"success": True, "message": f"{cow_id} a été supprimée."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@repro.route("/insemination", methods=["POST"])
def insemination():

    try:
        # Récupère la date
        date_obj = request.form["prescription_date"]
        # Récupération de l'id de la vache
        cow_id = int(request.form["id"])

        CowUtils.add_insemination(user_id=current_user.id, cow_id=cow_id, insemination=date_obj)

        return jsonify(
            {"success": True, "message": f"insemination {cow_id} ajouter avec succes"}
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur :{e}"})


@login_required
@repro.route("/ultrasound", methods=["POST"])
def ultrasound():
    try:
        # Récupération de l'id de la vache
        cow_id = int(request.form["id"])

        ultrasound = bool(request.form["ultrasound"])

        CowUtils.validated_ultrasound(user_id=current_user.id, cow_id=cow_id, ultrasound=ultrasound)

        success_message = f"l'echographie de {cow_id} a été {'valider' if ultrasound else 'invalider'} avec succes"
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur :{e}"})


@login_required
@repro.route("/show_dry")
def show_dry():
    try:
        dry_data = get_all_dry_date(user_id=current_user.id)
        return jsonify({"success": True, "dry": dry_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@login_required
@repro.route("/validate_dry", methods=["POST"])
def validate_dry():
    data = request.get_json()
    cow_id = data.get("cow_id")

    if not cow_id:
        return jsonify({"success": False, "message": "Aucune vache spécifiée."}), 400

    try:
        CowUtils.validated_dry(user_id=current_user.id, cow_id=cow_id)

        return jsonify({"success": True, "message": f"Tarissement validé pour {cow_id}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@login_required
@repro.route("/show_calving_preparation")
def show_calving_preparation():
    try:
        calving_preparation = get_all_calving_preparation_date(user_id=current_user.id)
        return jsonify({"success": True, "calving_preparation": calving_preparation})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@login_required
@repro.route("/validate_calving_preparation", methods=["POST"])
def validate_calving_preparation():
    data = request.get_json()
    cow_id = data.get("cow_id")
    lg.info(f"Validation de la préparation au vêlage pour la vache {cow_id}...")
    if not cow_id:
        return jsonify({"success": False, "message": "Aucune vache spécifiée."}), 400

    try:
        CowUtils.validated_calving_preparation(user_id=current_user.id, cow_id=cow_id)

        return jsonify({"success": True, "message": f"Tarissement validé pour {cow_id}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@login_required
@repro.route("/show_calving_date")
def show_calving_date():
    try:
        calving_data = get_all_calving_date(user_id=current_user.id)
        return jsonify({"success": True, "calving": calving_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@login_required
@repro.route("/upload_calf", methods=["POST"])
def upload_calf():
    try:
        # Récupération des données du formulaire
        borning = request.form["borning"]
        mother_id = int(request.form["mother_id"])
        calf_id = int(request.form["calf_id"])
        calving_date = request.form["calving_date"]
        if borning == "abortion":
            CowUtils.validated_calving(user_id=current_user.id,cow_id=mother_id, abortion=True)
            success_message = f"avortement de {mother_id} rensegné, courage"

        elif calf_id and calving_date:
            lg.info(f"Adding new calf {calf_id}...")
            CowUtils.validated_calving(user_id=current_user.id, cow_id=mother_id, abortion=False)
            calving_date = datetime.strptime(calving_date, "%Y-%m-%d").date()
            CowUtils.add_calf(user_id=current_user.id, calf_id=calf_id, born_date=calving_date)
            success_message = f"naissance de {calf_id} confirmé"
        else:
            raise ValueError('Renségner "Numéro Veau" et  "Date de velage"')

        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


# END  Reproduction form
