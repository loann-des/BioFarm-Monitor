from datetime import datetime
from io import BytesIO
import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    render_template,
    send_file,
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
@pharmacybp.route("/pharmacy/export-recap-cows", methods=["GET"])
def export_recap_cow():
    try :
        file_bytes = current_user.remaining_care_to_excel()
        return send_file(
            file_bytes,
            as_attachment=True,
            download_name="stock.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors du Telecargement: {e}"
        })


@login_required
@pharmacybp.route("/pharmacy/export-recap-pharmacy", methods=["Get"])
def export_recap_pharmacy():
    try :
        file_bytes = current_user.pharmacie_to_csv(datetime.now().year)
        return send_file(
            file_bytes,
            as_attachment=True,
            download_name="Recap_pharmacie.csv",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors du Telecargement: {e}"
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
    try:
        prescription = current_user.prescription_utils.get_all_prescriptions_cares()
        return jsonify({
            "success": True,
            "message": prescription
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des prescriptions : {e}"
        })


@login_required
@pharmacybp.route("/pharmacy/get-dlc-left", methods=["GET"])
def get_dlc_left():
    try:
        dlc = current_user.prescription_utils.get_all_dlc_cares()
        return jsonify({
            "success": True,
            "message": dlc
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des sorties pour dlc{e}"
        })


@login_required
@pharmacybp.route("/pharmacy/remove-prescription", methods=["POST"])
def remove_prescription():
    try:
        prescription_id = int(request.form["prescription_id"])
        current_user.prescription_utils.remove_prescription(prescription_id)
        return jsonify({
            "success": True,
            "message": "not impemented yet"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des prescriptions : {e}"
        })


@login_required
@pharmacybp.route("/pharmacy/change-prescription", methods=["POST"])
def change_prescription():
    try:
        # TODO
        return jsonify({
            "success": True,
            "message": "not impemented yet"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des prescriptions : {e}"
        })
