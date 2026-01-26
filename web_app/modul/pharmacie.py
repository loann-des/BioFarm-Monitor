# Pharmacie form
import logging as lg

from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for
)
from flask_login import login_required, current_user # type: ignore
from io import BytesIO

from ..connected_user import ConnectedUser
from web_app.fonction import (
    date_to_str,
)
from web_app.models import (
    CowUtils,
    PharmacieUtils,
    PrescriptionUtils,
    Traitement,
    UserUtils,
    Users
)


pharma = Blueprint('pharma', __name__)

current_user : ConnectedUser

@pharma.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for('auth.logout'))

@login_required
@pharma.route("/update_care", methods=["POST"])
def update_care():
    # TODO valider traitemment seulement si pas de bug (dernier opération)
    def extract_cares(form : dict):
        cares = {}
        for nb_care in range(current_user.get_pharma_len()):
            medic = form.get(f"medic_{nb_care+1}")
            quantite = form.get(f"medic_{nb_care+1}_nb")
            if medic and quantite:
                try:
                    if medic in cares:
                        raise ValueError(f"Médicament en double : {medic}")
                    qte_int = int(quantite)
                    cares[medic] = qte_int
                except ValueError:
                    lg.warning(f"Quantité invalide pour medic_{nb_care+1}: {quantite}")
        return cares


    try:
        # Récupération des données du formulaire
        cow_id = request.form["id"]
        care : Traitement = Traitement(
            date_traitement=request.form["care_date"],
            medicaments=extract_cares(request.form),
            annotation=request.form["care_info"]
            )
        
        # care["medicaments"] = extract_cares(request.form)

        # care["date_traitement"] = request.form["care_date"]

        # care["annotation"] = request.form["care_info"]



        lg.info(f"update care{cow_id}...")

        remain_care = CowUtils.add_cow_care(user_id=current_user.id, cow_id=cow_id, cow_care=care) # type: ignore

        success_message = f"il reste : {remain_care[0]} traitement autoriser en bio jusque'au {date_to_str(remain_care[1])} pour {cow_id}." # type: ignore
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@pharma.route("/add_medic_in_pharma_list", methods=["POST"])
def add_medic_in_pharma_list():

    try:
        # Récupération des données du formulaire
        medic = request.form["medic"]
        mesur = request.form["medic_unit"]
        lg.info(f"Ajout de {medic} a l'armoire a pharmacie...")

        UserUtils.add_medic_in_pharma_list(user_id=current_user.id, medic=medic, mesur=mesur) # type: ignore

                # Retourne un JSON avec l'URL de redirection
        return jsonify({
            "success": True,
            "message": f"{medic} a été ajouté à l'armoire à pharmacie.",
            "redirect": url_for("views.pharmacie")
        })

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@pharma.route("/add_prescription", methods=["POST"])
def add_prescription():
    try:
        # Récupère et parse la date
        prescription_date_str = request.form["prescription_date"]
        date_obj = datetime.strptime(prescription_date_str, "%Y-%m-%d").date()

        # Récupère les médicaments et quantités
        cares: dict[str, int] = {}
        for nb_care in range(current_user.get_pharma_len()):
            medic = request.form.get(f"medic_{nb_care+1}")
            quantite = request.form.get(f"medic_{nb_care+1}_nb")

            if medic and quantite:
                qte_int = int(quantite)
                if qte_int < 0:
                    lg.error(
                        f"Quantité negative invalide pour medic_{nb_care+1}: {quantite}"
                    )
                    raise ValueError(
                        f"Le médicament '{medic}' en quantité negative est interdit."
                    )
                if qte_int > 0:
                    if medic in cares:
                        lg.error(
                            f"Quantité invalide pour medic_{nb_care+1}: {quantite}"
                        )
                        raise ValueError(f"Le médicament '{medic}' est en double.")
                    cares[medic] = qte_int

        if not cares:
            raise ValueError(
                "Veuillez renseigner au moins un médicament avec une quantité valide."
            )

        PrescriptionUtils.add_prescription(user_id=current_user.id, date=date_obj, care_items=cares) # type: ignore

        return jsonify({"success": True, "message": "Ordonnance ajoutée avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@pharma.route("/add_dlc_left", methods=["POST"])
def add_dlc_left():

    try:
        # Récupère et parse la date
        dlc_left_date_str = request.form["prescription_date"]
        date_obj = datetime.strptime(dlc_left_date_str, "%Y-%m-%d").date()

        # Récupère les médicaments et quantités
        cares: dict[str, int] = {}
        for nb_care in range(current_user.get_pharma_len()):
            medic = request.form.get(f"medic_{nb_care+1}")
            quantite = request.form.get(f"medic_{nb_care+1}_nb")

            if medic and quantite:
                qte_int = int(quantite)
                if qte_int > 0:  # ignor les chaps vide
                    if medic in cares:
                        lg.error(
                            f"Quantité invalide pour medic_{nb_care+1}: {quantite}"
                        )
                        raise ValueError(f"Le médicament '{medic}' est en double.")
                    cares[medic] = qte_int

        if not cares:
            raise ValueError(
                "Veuillez renseigner au moins un médicament avec une quantité valide."
            )

        PrescriptionUtils.add_dlc_left(user_id=current_user.id, date=date_obj, care_items=cares)

        return jsonify({"success": True, "message": "Medicament sortie avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@pharma.route("/get_stock", methods=["GET"])
def get_stock():
    try:
        year = datetime.now().year  #on récupère l'année
        stock_data = current_user.remaining_pharmacie_stock(year=year)
        return jsonify({"success": True, "stock": stock_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@login_required
@pharma.route("/stock_details", methods=["GET"])
def stock_details():
    return render_template("stock_details.html", history_pharmacie=get_history_pharmacie(user_id=current_user.id)) # type: ignore


@login_required
@pharma.route("/download", methods=["GET", "POST"])
def download():
    lg.info("export-stock")
    try:
        year = int(request.form["export_year"])  # CHAMP CORRIGÉ ICI
        csv_str = current_user.pharmacie_to_csv(year=year)

        # Encodage du CSV en bytes pour envoi en tant que fichier
        csv_bytes = BytesIO(csv_str.encode("utf-8"))

        lg.info(f"Téléchargement du CSV pour {year}")

        return send_file(
            csv_bytes,
            download_name=f"pharmacie_{year}.csv",
            as_attachment=True,
            mimetype="text/csv",
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


@login_required
@pharma.route("/download_remaining_care", methods=["GET", "POST"])
def download_remaining_care():
    try:
        excel_io = remaining_care_to_excel(user_id=current_user.id) # type: ignore

        return send_file(
            excel_io, # type: ignore
            download_name="traitement.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


# END Pharmacie form
