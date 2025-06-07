from datetime import datetime
from flask import Flask, jsonify, render_template, request
import logging as lg

app = Flask(__name__)
app.config.from_object("config.config")


@app.route("/", methods=["GET"])
def index():
    return render_template("upload.html")


@app.route("/upload_cow", methods=["POST"])
def upload_cow():
    #TODO js upload_cow
    from .models import upload_cow as upd

    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])

        lg.info(f"Adding new cow {id}...")

        upd(id=id, traitement=None)

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


@app.route("/update_care", methods=["POST"])
def update_care():
    #TODO js update_care
    # TODO reajuster
    from .models import update_care as upc

    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])
        care_medic = request.form["care_medic"]
        care_date_str = request.form["care_date"]
        care_info = request.form["care_info"]

        # Conversion des champs
        care = (care_medic, datetime.strptime(care_date_str, "%Y-%m-%d").date())

        lg.info(f"update care{id}...")

        remain_care = upc(id=id, care=care)

        success_message = (
            f"il reste : {remain_care} traitement autoriser en bio pour {id}."
        )
        return render_template(
            "upload.html",
            success_message=success_message,
            success_message_New_Care=success_message,
            anchor="Care",
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template(
            "upload.html",
            error_message=error_message,
            error_message_New_Care=error_message,
            anchor="Care",
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


from flask import request, render_template
from datetime import datetime
import logging

@app.route("/add_prescription", methods=["POST"])
def add_prescription():
    #TODO add_prescription clean
    import logging
    from .fonction import get_pharma_len
    from .models import add_prescription as add_pres
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        logging.debug(f"Données reçues: {request.form}")

        prescription_date_str = request.form["prescription_date"]
        date = datetime.strptime(prescription_date_str, "%Y-%m-%d").date()

        cares = []
        for nb_care in range(get_pharma_len()):
            medic = request.form.get(f"medic_{nb_care+1}")
            quantite = request.form.get(f"medic_{nb_care+1}_nb")

            # On ne garde que les paires non vides et quantite > 0
            if medic and quantite:
                try:
                    qte_int = int(quantite)
                    if qte_int > 0:
                        cares.append({"medicament": medic, "quantite": qte_int})
                except ValueError:
                    logging.warning(f"Quantité invalide pour medic_{nb_care+1}: {quantite}")

        if not cares:
            raise ValueError("Veuillez renseigner au moins un médicament avec une quantité valide.")

        add_pres(date=date, care_items=cares)

        return jsonify({"success": True, "message": "Ordonnance ajoutée avec succès."})
    except Exception as e:
        logging.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@app.route("/add_medic_in_pharma_liste", methods=["POST"])
def add_medic_in_pharma_liste():
    from .models import add_medic_in_pharma_liste as adm

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

