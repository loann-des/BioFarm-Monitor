from datetime import datetime
from io import BytesIO
from flask import Flask, jsonify, render_template, request, send_file
import logging as lg

app = Flask(__name__)
app.config.from_object("config.config")


from .fonction import *
from .models import CowUntils, PrescriptionUntils, PharmacieUtils, UserUtils

# TODO edit Hystory
# TODO gestion des log


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/user_setting", methods=["POST"])
# TODO recalculer velage si changer
def user_setting():
    try:
        dry_time = request.form["dry_time"]
        calving_preparation_time = request.form["calving_preparation_time"]

        UserUtils.set_user_setting(
            dry_time=dry_time, calving_preparation=calving_preparation_time
        )

        return jsonify({"success": True, "message": "setting mis a jours."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


# Pharmatie root
@app.route("/pharmacie", methods=["GET"])
def pharmacie():
    return render_template("pharmacie.html")


@app.route("/update_care", methods=["POST"])
def update_care():

    def extract_cares(form, pharma_len):
        cares = {}
        for nb_care in range(pharma_len):
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

    def extract_care_date_and_info(form):
        care_date_str = form["care_date"]
        care_info = form["care_info"]
        care_date = datetime.strptime(care_date_str, "%Y-%m-%d").date()
        return care_date, care_info

    try:
        # Récupération des données du formulaire
        id_cow = request.form["id"]
        cares = extract_cares(request.form, get_pharma_len())
        care_date, care_info = extract_care_date_and_info(request.form)
        care = (care_date, cares, care_info)

        lg.info(f"update care{id_cow}...")

        remain_care = CowUntils.update_care(id=id_cow, cow_care=care)

        success_message = f"il reste : {remain_care[0]} traitement autoriser en bio jusque'au {remain_care[1]} pour {id_cow}."
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_prescription", methods=["POST"])
def add_prescription():
    try:
        # Récupère et parse la date
        prescription_date_str = request.form["prescription_date"]
        date_obj = datetime.strptime(prescription_date_str, "%Y-%m-%d").date()

        # Récupère les médicaments et quantités
        cares: dict[str, int] = {}
        for nb_care in range(get_pharma_len()):
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

        PrescriptionUntils.add_prescription(date=date_obj, care_items=cares)

        return jsonify({"success": True, "message": "Ordonnance ajoutée avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_dlc_left", methods=["POST"])
def add_dlc_left():

    try:
        # Récupère et parse la date
        dlc_left_date_str = request.form["prescription_date"]
        date_obj = datetime.strptime(dlc_left_date_str, "%Y-%m-%d").date()

        # Récupère les médicaments et quantités
        cares: dict[str, int] = {}
        for nb_care in range(get_pharma_len()):
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

        PrescriptionUntils.add_dlc_left(date=date_obj, care_items=cares)

        return jsonify({"success": True, "message": "Medicament sortie avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_medic_in_pharma_list", methods=["POST"])
def add_medic_in_pharma_list():

    try:
        # Récupération des données du formulaire
        medic = request.form["medic"]
        lg.info(f"Ajout de {medic} a l'armoire a pharmacie...")

        PrescriptionUntils.add_medic_in_pharma_list(medic=medic)

        success_message = f"{medic} a été ajout à l'armoire a pharmacie."
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/init_stock", methods=["POST"])
def init_stock():
    try:
        # Récupère et parse la date
        year = request.form["prescription_date"]

        # Récupère les médicaments et quantités
        remaining_stock: dict[str, int] = {}
        for nb_care in range(get_pharma_len()):
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

        PharmacieUtils.upload_pharmacie_year(year=year, remaining_stock=remaining_stock)

        return jsonify(
            {"success": True, "message": "pharmacie initialiser avec succès."}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/get_stock", methods=["GET"])
def get_stock():
    try:
        year = datetime.now().year  # on récupère l'année en paramètre
        stock_data = remaining_pharmacie_stock(year)
        return jsonify({"success": True, "stock": stock_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/stock_details", methods=["GET"])
def stock_details():
    return render_template("stock_details.html")


@app.route("/download/", methods=["GET", "POST"])
def download():
    print(request.form)
    try:
        year = int(request.form["export_year"])  # CHAMP CORRIGÉ ICI
        csv_str = pharmacie_to_csv(year)

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


# END Pharmatie root

# Reproduction root


@app.route("/reproduction", methods=["GET"])
def reproduction():
    return render_template("reproduction.html")


@app.route("/upload_cow", methods=["POST"])
def upload_cow():
    # TODO gestion veaux upload_cow
    try:
        # Récupération des données du formulaire
        cow_id = int(request.form["id"])

        lg.info(f"Adding new cow {cow_id}...")

        CowUntils.upload_cow(id=cow_id, born_date=datetime.now())

        return jsonify(
            {"success": True, "message": "La vache a été ajoutée avec succès !"}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/remove_cow", methods=["POST"])
def remove_cow():

    try:
        # Récupération des données du formulaire
        cow_id = int(request.form["id"])

        lg.info(f"supresion de {cow_id}...")

        CowUntils.remove_cow(id=cow_id)

        return jsonify({"success": True, "message": f"{cow_id} a été supprimée."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/insemination", methods=["POST"])
def insemination():

    try:
        # Récupère et parse la date
        dlc_left_date_str = request.form["prescription_date"]
        date_obj = datetime.strptime(dlc_left_date_str, "%Y-%m-%d").date()

        # Récupération de l'id de la vache
        cow_id = int(request.form["id"])

        CowUntils.add_insemination(id=cow_id, insemination=date_obj)

        return jsonify(
            {"success": True, "message": f"insemination {cow_id} ajouter avec succes"}
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur :{e}"})


@app.route("/ultrasound", methods=["POST"])
def ultrasound():
    try:
        # Récupération de l'id de la vache
        cow_id = int(request.form["id"])

        ultrasound = bool(request.form["ultrasound"])

        CowUntils.validated_ultrasound(id=cow_id, ultrasound=ultrasound)

        success_message = f"l'echographie de {cow_id} a été {'valider' if ultrasound else 'invalider'} avec succes"
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur :{e}"})


@app.route("/show_dry")
def show_dry():
    try:
        dry_data = get_all_dry_date()
        return jsonify({"success": True, "dry": dry_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/show_calving_preparation")
def show_calving_preparation():
    try:
        calving_preparation = get_all_calving_preparation_date()
        return jsonify({"success": True, "calving_preparation": calving_preparation})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/show_calving_date")
def show_calving_date():
    try:
        calving_data = get_all_calving_date()
        return jsonify({"success": True, "calving": calving_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/upload_calf", methods=["POST"])
def upload_calf():
    # TODO gestion veaux upload_cow
    try:
        # Récupération des données du formulaire
        borning = request.form["borning"]
        mother_id = request.form["mother_id"]
        calf_id = request.form["calf_id"]
        calving_date = request.form["calving_date"]
        if borning == "abortion" :
            CowUntils.validated_calving(cow_id=mother_id,abortion=True)
            success_message = f"avortement de {mother_id} rensegné, courage"
        
        elif (calf_id and calving_date):
            lg.info(f"Adding new calf {calf_id}...")
            CowUntils.validated_calving(cow_id=mother_id,abortion=False)
            calving_date = datetime.strptime(calving_date, "%Y-%m-%d").date()
            CowUntils.add_calf(calf_id=calf_id, born_date=calving_date)
            success_message = f"naissance de {calf_id} confirmé"
        else :
            raise ValueError(f"Renségner \"Numéro Veau\" et  \"Date de velage\"")


        return jsonify(
            {"success": True, "message": success_message}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})

# END  Reproduction root


app.jinja_env.globals.update(get_pharma_list=get_pharma_list)
app.jinja_env.globals.update(get_pharma_len=get_pharma_len)
app.jinja_env.globals.update(get_hystory_pharmacie=get_hystory_pharmacie)
