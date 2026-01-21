from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import CowUtils, Users, db
import logging as lg
from flask_login import login_required, current_user, AnonymousUserMixin # type: ignore
from datetime import datetime

# TODO tout retaper/reparé ici 



cow_liste = Blueprint('cow_liste', __name__)

current_user : Users

@cow_liste.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for('auth.logout'))

@login_required
@cow_liste.route("/cow_liste/view_cow/<int:cow_id>", methods=["GET", "POST"])
def view_cow(cow_id):
    print(">>> view_cow called 1")
    if cow := CowUtils.get_cow(user_id=current_user.id, cow_id=cow_id):
        print(">>> view_cow called")
        # web_app/templates/cow_details.html
        return render_template("cow_details.html", cow=cow)
    else:
        return "Vache introuvable", 404

@login_required
@cow_liste.route("/cow_liste/edit_cow/<int:cow_id>", methods=["GET", "POST"])
def edit_cow(cow_id):
    return render_template("cow_edit.html", cow=CowUtils.get_cow(user_id=current_user.id, cow_id=cow_id))


@login_required
@cow_liste.route("/cow_liste/suppress_cow/<int:cow_id>", methods=["POST"])
def suppress_cow(cow_id):
    # TODO Ajout ms confirmation avant suppression
    lg.info(f"Suppression de la vache {cow_id}...")
    try:
        CowUtils.suppress_cow(user_id=current_user.id, cow_id=cow_id)
        return jsonify({"success": True, "message": f"Vache {cow_id} supprimée."})
    except Exception as e:
        lg.error(f"Erreur pendant la suppression de la vache {cow_id}: {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


# END cow_liste form


# cow_edit form


@login_required
@cow_liste.route("/update_cow_details/<int:cow_id>", methods=["POST"])
def update_cow_details(cow_id):
    # Récupération des données du formulaire
    in_farm = bool(request.form.get("in_farm"))
    born_date_str = request.form.get("born_date")
    born_date = datetime.strptime(born_date_str, "%Y-%m-%d").date() # type: ignore

    # Préparation des kwargs à passer à la fonction update_cow
    update_data = {
        "in_farm": in_farm,
        "born_date": born_date,
    }

    # Récupération des infos supplémentaires dynamiques
    info_count = int(request.form.get("info_count", 0))
    info_list = []
    for i in range(1, info_count + 1):
        date = request.form.get(f"info_date_{i}")
        info = request.form.get(f"info_{i}")
        if date and info:
            info_list.append((date, info))

    update_data["info"] = info_list  # ou adapte le nom de champ selon ton modèle

    try:
        CowUtils.update_cow(cow_id, **update_data)
        flash("Vache mise à jour avec succès.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("edit_cow", cow_id=cow_id))

@login_required
@cow_liste.route("/update_cow_care/<int:cow_id>/<int:care_index>", methods=["POST"])
def update_cow_care(cow_id, care_index):

    # Récupération des données du formulaire
    date_str = request.form.get("care_date")
    new_date = datetime.strptime(date_str, "%Y-%m-%d").date() # type: ignore
    new_info = request.form.get("care_info", "")

    # Récupération des médicaments
    meds = {}
    i = 1
    while med := request.form.get(f"medic_{i}"):
        if qty := request.form.get(f"medic_{i}_nb"):
            meds[med] = int(qty)
        i += 1

    CowUtils.update_cow_care(
        user_id=current_user.id, cow_id=cow_id, care_index=care_index, new_care=(new_date, meds, new_info)
    )

    flash("Soin modifié avec succès", "success")
    return redirect(url_for("edit_cow", cow_id=cow_id))  # ou autre vue

@login_required
@cow_liste.route('/delete_cow_care/<int:cow_id>/<int:care_index>', methods=['POST'])
def delete_cow_care(cow_id, care_index):
    try:
        CowUtils.delete_cow_care(cow_id=cow_id, care_index=care_index)
        flash("Soin supprimé.")
    except IndexError:
        flash("Soin introuvable.")
    return redirect(url_for('edit_cow', cow_id=cow_id))

@login_required
@cow_liste.route("/update_cow_reproduction/<int:cow_id>/<int:repro_index>", methods=["POST"])
def update_cow_reproduction(cow_id, repro_index):
    # TODO recalculer sur modif

    try:
        # Récupérer les données du formulaire
        insemination = request.form.get("insemination")
        ultrasound = request.form.get("ultrasound")
        dry = request.form.get("dry")
        calving_preparation = request.form.get("calving_preparation")
        calving_date = request.form.get("calving_date")
        calving = request.form.get("calving")
        abortion = request.form.get("abortion")
        info = request.form.get("info")

        # Convertir les chaînes en dates et booléens
        new_repro = {
            "insemination": parse_date(insemination),
            "ultrasound": parse_bool(ultrasound),
            "dry": parse_date(dry),
            "calving_preparation": parse_date(calving_preparation),
            "calving_date": parse_date(calving_date),
            "calving": parse_bool(calving),
            "abortion": parse_bool(abortion),
        }

        # Mettre à jour la reproduction et l'info complémentaire
        CowUtils.update_cow_reproduction(
            cow_id=cow_id, repro_index=repro_index, new_repro=(new_repro, info)
        )

    except (ValueError, KeyError) as e:
        flash(f"Erreur lors de la mise à jour: {e}", "error")
    except Exception as e:
        views.logger.exception("Unexpected error during cow reproduction update")
        raise

    return redirect(url_for("cow_details", cow_id=cow_id))

@login_required
@cow_liste.route('/delete_cow_reproduction/<int:cow_id>/<int:repro_index>', methods=['POST'])
def delete_cow_reproduction(cow_id, repro_index):
    try:
        CowUtils.delete_cow_reproduction(cow_id=cow_id, repro_index=repro_index)
        flash("Reproduction supprimée.")
    except IndexError:
        flash("Reproduction introuvable.")
    return redirect(url_for('edit_cow', cow_id=cow_id))

# END cow_edit form
