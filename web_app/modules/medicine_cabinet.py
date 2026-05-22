from datetime import datetime
import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    render_template,
    url_for
)

from flask_login import login_required, current_user  # type: ignore

from web_app.fonction import my_strftime, parse_date
from web_app.models.type_dict import Reproduction, Traitement

from ..connnected_user_web.connected_user import ConnectedUser

pharmacybp = Blueprint("pharmacy", __name__)

current_user: ConnectedUser


@login_required
@pharmacybp.route("/pharmacy/add-prescriptions", methods=["POST"])
def add_prescription():
    try:
        date = parse_date(request.form["date"])
        medicaments = request.form.getlist("medication")
        doses = request.form.getlist("dose")
        care_items = {medicament: int(dose)
                      for medicament, dose in zip(medicaments, doses)}

        current_user.prescription_utils.add_prescription(date, care_items)
        return jsonify({
            "success": True,
            "message": "prescription ajouter avec succes"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de l'ajout de prescription : {e}"
        })


@login_required
@pharmacybp.route("/pharmacy/add-dlc-left", methods=["POST"])
def add_dlc_left():
    try:
        date = parse_date(request.form["date"])
        medicaments = request.form.getlist("medication")
        doses = request.form.getlist("dose")
        care_items = {medicament: int(dose)
                      for medicament, dose in zip(medicaments, doses)}

        current_user.prescription_utils.add_dlc_left(date, care_items)
        return jsonify({
            "success": True,
            "message": "sortie pour dlc ajouter avec succes"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la sortie pour dlc : {e}"
        })


@login_required
@pharmacybp.route("/pharmacy/export-recap-cows", methods=["POST"])
def export_recap_cow():
    return jsonify({
        "success": True,
        "message": "not implemented yet"
    })


@login_required
@pharmacybp.route("/pharmacy/export-recap-pharmacy", methods=["POST"])
def export_recap_pharmacy():
    return jsonify({
        "success": True,
        "message": "not implemented yet"
    })


@login_required
@pharmacybp.route("/pharmacy/get-stock", methods=["GET"])
def get_stock():
    try:
        stock = current_user.get_pharmacie_year(
            datetime.now().year).remaining_stock
        return jsonify({
            "success": True,
            "message": stock
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des stock: {e}"
        })


@login_required
@pharmacybp.route("/pharmacy/get-prescription", methods=["GET"])
def get_prescription():
    try :
        prescription = current_user.prescription_utils.get_all_prescriptions_cares()
        return jsonify({
            "success": True,
            "message": prescription
        })
    except Exception as e :
        return jsonify({
            "success": False,
            "message": "not implemented yet"
        })


@login_required
@pharmacybp.route("/pharmacy/get-dlc-left", methods=["POST"])
def get_dlc_left():
    return jsonify({
        "success": True,
        "message": "not implemented yet"
    })
