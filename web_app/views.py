from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
import logging as lg

app = Flask(__name__)
app.config.from_object("config.config")

mail = Mail(app)

@app.route("/" ,  methods=["GET"])
def index():
    return render_template("upload.html")

# @app.route("/upload-page", methods=["GET"])
# def upload():
#     return render_template("upload.html")

@app.route("/upload_cow", methods=["POST"])
def upload_cow() :
    from .models import upload_cow as upd
    from .models import Race
    try:
        # Récupération des données du formulaire
        id = int(request.form["id"])
        race_str = request.form["race"]
        date_str = request.form["date_naissance"]

        # Conversion des champs
        race = Race[race_str]  # Ex: "Brune" -> Race.Brune
        date_naissance = datetime.strptime(date_str, "%Y-%m-%d").date()

        lg.info(f"Adding new cow {id}...")
        
        upd(id=id, race=race, date_naissance=date_naissance, traitement=None)
        
        return redirect(url_for("index"))

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return f"Erreur : {str(e)}", 500
