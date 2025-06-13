from datetime import datetime
from flask import Flask, jsonify, render_template, request
import logging as lg

app = Flask(__name__)
app.config.from_object("config.config")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Pharmatie root
@app.route("/pharmacie", methods=["GET"])
def pharmacie():
    return render_template("pharmacie.html")


@app.route("/update_care", methods=["POST"])
def update_care():
    from .models import update_care as upc
    from .fonction import get_pharma_len

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

        remain_care = upc(id=id_cow, cow_care=care)

        success_message = (
            f"il reste : {remain_care[0]} traitement autoriser en bio jusque'au {remain_care[1]} pour {id_cow}."
        )
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_prescription", methods=["POST"])
def add_prescription():
    from .fonction import get_pharma_len
    from .models import add_prescription as add_pres

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
                    lg.error(f"Quantité negative invalide pour medic_{nb_care+1}: {quantite}")
                    raise ValueError(f"Le médicament '{medic}' en quantité negative est interdit.")
                if qte_int > 0:
                    if medic in cares:
                        lg.error(f"Quantité invalide pour medic_{nb_care+1}: {quantite}")
                        raise ValueError(f"Le médicament '{medic}' est en double.")
                    cares[medic] = qte_int

        if not cares:
            raise ValueError("Veuillez renseigner au moins un médicament avec une quantité valide.")

        add_pres(date=date_obj, care_items=cares)

        return jsonify({"success": True, "message": "Ordonnance ajoutée avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_dlc_left", methods=["POST"])
def add_dlc_left():
    from .fonction import get_pharma_len
    from .models import add_dlc_left as dlc_left

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
                if qte_int > 0: # ignor les chaps vide
                    if medic in cares:
                        lg.error(f"Quantité invalide pour medic_{nb_care+1}: {quantite}")
                        raise ValueError(f"Le médicament '{medic}' est en double.")
                    cares[medic] = qte_int

        if not cares:
            raise ValueError("Veuillez renseigner au moins un médicament avec une quantité valide.")

        dlc_left(date=date_obj, care_items=cares)

        return jsonify({"success": True, "message": "Medicament sortie avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_medic_in_pharma_list", methods=["POST"])
def add_medic_in_pharma_list():
    from .models import add_medic_in_pharma_list as adm

    try:
        # Récupération des données du formulaire
        medic = request.form["medic"]
        lg.info(f"Ajout de {medic} a l'armoire a pharmacie...")

        adm(medic=medic)

        success_message = f"{medic} a été ajout à l'armoire a pharmacie."
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route('/init_stock', methods=["POST"])
def init_stock():
    from .fonction import get_pharma_len
    from .models import upload_pharmacie_year as upy

    try:
        # Récupère et parse la date
        year = request.form["prescription_date"]

        # Récupère les médicaments et quantités
        remaining_stock : dict[str: int] = {}
        for nb_care in range(get_pharma_len()):
            medic = request.form.get(f"medic_{nb_care+1}")
            quantite = request.form.get(f"medic_{nb_care+1}_nb")

            if medic and quantite:
                qte_int = int(quantite)
                if qte_int > 0: # ignor les chaps vide
                    if medic in remaining_stock:
                        lg.error(f"Quantité invalide pour medic_{nb_care+1}: {quantite}")
                        raise ValueError(f"Le médicament '{medic}' est en double.")
                    remaining_stock[medic] = qte_int

        if not remaining_stock:
            raise ValueError("Veuillez renseigner au moins un médicament avec une quantité valide.")

        upy(year=year, remaining_stock=remaining_stock)

        return jsonify({"success": True, "message": "pharmacie initialiser avec succès."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/get_stock", methods=["GET"])
def get_stock():
    from .fonction import remaining_pharmacie_stock  # ta fonction qui renvoie un dict {medicament: quantité}
    
    try:
        year = datetime.now().year  # on récupère l'année en paramètre
        stock_data = remaining_pharmacie_stock(year)
        return jsonify({"success": True, "stock": stock_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/stock_details')
def stock_details():
    return render_template("stock_details.html")

# END Pharmatie root

# Reproduction root

@app.route("/reproduction", methods=["GET"])
def reproduction():
    return render_template("reproduction.html")

@app.route("/upload_cow", methods=["POST"])
def upload_cow():
    #TODO js upload_cow
    from .models import upload_cow as upd

    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])

        lg.info(f"Adding new cow {id}...")

        upd(id=id, born_date=datetime.now())

        success_message = "La vache a été ajoutée avec succès !"
        return render_template(
            "upload.html",
            success_message=success_message,
            success_message_New_Cow=success_message,
            anchor="New_Cow",
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template(
            "upload.html",
            error_message=error_message,
            error_message_New_Cow=error_message,
            anchor="New_Cow",
        )


@app.route("/remove_cow", methods=["POST"])
def remove_cow():
    #TODO js remove_cow
    from .models import remove_cow as rmc

    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])

        lg.info(f"supresion de {id}...")

        rmc(id=id)

        success_message = f"{id} a été supprimée."
        return render_template(
            "upload.html",
            success_message=success_message,
            success_message_Remove=success_message,
            anchor="Remove",
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template(
            "upload.html",
            error_message=error_message,
            error_message_Remove=error_message,
            anchor="Remove",
        )


# END  Reproduction root
