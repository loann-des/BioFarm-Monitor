# Pharmacie form
from datetime import datetime
from io import BytesIO
from flask import Blueprint, jsonify, redirect, render_template, request, send_file, url_for
import logging as lg
from flask_login import login_required, current_user


from web_app.fonction import get_pharma_len, pharmacie_to_csv, remaining_care_to_excel, remaining_pharmacie_stock, strftime
from web_app.models import CowUntils, PharmacieUtils, PrescriptionUntils, Traitement, UserUtils, Users


pharma = Blueprint('pharma', __name__)

current_user : Users

@login_required
@pharma.route("/update_care", methods=["POST"])
def update_care():
    # TODO valider traitemment seulement si pas de bug (dernier opération)
    def extract_cares(form : dict):
        cares = {}
        for nb_care in range(get_pharma_len(current_user.id)):
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
        care : Traitement = Traitement()
        care["medicaments"] = extract_cares(request.form)
        # print(request.form["care_date"])
        # date_obj = datetime.strptime(request.form["care_date"], "%Y-%m-%d").date()
        care["date_traitement"] = request.form["care_date"]
        # print(date_obj)
        # print(datetime.now())
        # print(datetime.now().strftime("%Y-%m-%d"))
        care["annotation"] = request.form["care_info"]



        lg.info(f"update care{cow_id}...")

        remain_care = CowUntils.add_cow_care(user_id=current_user.id, cow_id=cow_id, cow_care=care)

        success_message = f"il reste : {remain_care[0]} traitement autoriser en bio jusque'au {remain_care[1]} pour {cow_id}."
        return jsonify({"success": True, "message": success_message})

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
        for nb_care in range(get_pharma_len(user_id=current_user.id)):
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

        PrescriptionUntils.add_prescription(user_id=current_user.id, date=date_obj, care_items=cares)

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
        for nb_care in range(get_pharma_len(user_id=current_user.id)):
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

        PrescriptionUntils.add_dlc_left(user_id=current_user.id, date=date_obj, care_items=cares)

        return jsonify({"success": True, "message": "Medicament sortie avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required #TODO bougé sur le home pour l'init
@pharma.route("/add_medic_in_pharma_list", methods=["POST"])
def add_medic_in_pharma_list():

    try:
        # Récupération des données du formulaire
        medic = request.form["medic"]
        mesur = request.form["medic_unit"]
        lg.info(f"Ajout de {medic} a l'armoire a pharmacie...")

        UserUtils.add_medic_in_pharma_list(user_id=current_user.id, medic=medic, mesur=mesur)

                # Retourne un JSON avec l'URL de redirection
        return jsonify({
            "success": True,
            "message": f"{medic} a été ajouté à l'armoire à pharmacie.",
            "redirect": url_for("views.pharmacie")
        })

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required #TODO bougé sur le home pour l'init
@pharma.route("/init_stock", methods=["POST"])
def init_stock():
    try:
        # Récupère et parse la date
        year = request.form["prescription_date"]

        # Récupère les médicaments et quantités
        remaining_stock: dict[str, int] = {}
        for nb_care in range(get_pharma_len(current_user.id)):
            medic = request.form.get(f"medic_{nb_care+1}")
            quantite = request.form.get(f"medic_{nb_care+1}_nb")

            if medic and quantite:
                qte_int = int(quantite)
                if qte_int > 0:  # ignor les chaps vide
                    if medic in remaining_stock:
                        lg.error(
                            f"Quantité invalide pour medic_{nb_care+1}: {quantite}"
                        )
                        raise ValueError(f"Le médicament '{medic}' est en double.")
                    remaining_stock[medic] = qte_int

        if not remaining_stock:
            raise ValueError(
                "Veuillez renseigner au moins un médicament avec une quantité valide."
            )

        PharmacieUtils.upload_pharmacie_year(user_id=current_user.id, year=year, remaining_stock=remaining_stock)

        return jsonify(
            {"success": True, "message": "pharmacie initialiser avec succès."}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@pharma.route("/get_stock", methods=["GET"])
def get_stock():
    try:
        year = datetime.now().year  #on récupère l'année
        stock_data = remaining_pharmacie_stock(user_id=current_user.id, year=year)
        return jsonify({"success": True, "stock": stock_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@login_required
@pharma.route("/stock_details", methods=["GET"])
def stock_details():
    return render_template("stock_details.html")


@login_required
@pharma.route("/download", methods=["GET", "POST"])
def download():
    lg.info("export-stock")
    try:
        year = int(request.form["export_year"])  # CHAMP CORRIGÉ ICI
        csv_str = pharmacie_to_csv(user_id=current_user.id, year=year)

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
        excel_io = remaining_care_to_excel()

        return send_file(
            excel_io,
            download_name="traitement.xlsx",
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400


# END Pharmacie form