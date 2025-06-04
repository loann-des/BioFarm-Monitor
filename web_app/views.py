from datetime import datetime
from flask import Flask, render_template, request
import logging as lg

app = Flask(__name__)
app.config.from_object("config.config")

@app.route("/" ,  methods=["GET"])
def index():
    return render_template("upload.html")

# @app.route("/upload-page", methods=["GET"])
# def upload():
#     return render_template("upload.html")

@app.route("/upload_cow", methods=["POST"])
def upload_cow() :
    from .models import upload_cow as upd
    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])

        lg.info(f"Adding new cow {id}...")
        
        upd(id=id, traitement=None)
        
        success_message = "La vache a été ajoutée avec succès !"
        return render_template("upload.html", success_message=success_message , success_message_New_Cow=success_message, anchor="New_Cow")

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template("upload.html", error_message=error_message, error_message_New_Cow=error_message, anchor="New_Cow")
    
@app.route("/update_care", methods=["POST"])
def update_care() :
    from .models import update_care as upc
    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])
        care_medic = request.form["care_medic"]
        care_date_str = request.form["care_date"]
        care_info = request.form["care_info"]

        # Conversion des champs
        care = (care_medic,
                datetime.strptime(care_date_str, "%Y-%m-%d").date()
                )

        lg.info(f"update care{id}...")
        
        remain_care = upc(id=id, care=care)
        
        success_message = f"il reste : {remain_care} traitement autoriser en bio pour {id}."
        return render_template("upload.html", success_message=success_message, success_message_New_Care=success_message, anchor="Care")

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template("upload.html", error_message=error_message,  error_message_New_Care=error_message, anchor="Care")
    
@app.route("/remove_cow", methods=["POST"])
def remove_cow() :
    from .models import remove_cow as rmc
    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])

        lg.info(f"supresion de {id}...")
        
        rmc(id=id)
        
        success_message = f"{id} a été supprimée."
        return render_template("upload.html", success_message=success_message, success_message_Remove=success_message,anchor="Remove" )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template("upload.html", error_message=error_message, error_message_Remove=error_message, anchor="Remove")

@app.route("/add_prescription", methods=["POST"])
def add_prescription() :
    from .models import remove_cow as rmc
    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])

        lg.info(f"supresion de {id}...")
        
        rmc(id=id)
        
        success_message = f"{id} a été supprimée."
        return render_template("upload.html", success_message=success_message, success_message_Remove=success_message,anchor="Remove" )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        error_message = f"Erreur : {str(e)}"
        return render_template("upload.html", error_message=error_message, error_message_Remove=error_message, anchor="Remove")
