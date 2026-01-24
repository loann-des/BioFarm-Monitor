import logging as lg
import pandas as pd

from datetime import datetime
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user, AnonymousUserMixin # type: ignore
from io import BytesIO

from ..fonction import *
from ..models import CowUtils, UserUtils, Users

views = Blueprint('views', __name__)

# TODO edit
# TODO gestion des log
# TODO historique commande
# TODO reintroduction d'une vache


current_user : Users

@views.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for('auth.logout'))

@login_required
@views.route("/", methods=["GET","POST"])
def index():
    return render_template("index.html",user=current_user)


@login_required
@views.route("/reproduction", methods=["GET"])
def reproduction():
    return render_template("reproduction.html")


@login_required
@views.route("/pharmacie", methods=["GET"])
def pharmacie():
    return render_template("pharmacie.html", pharma_list = get_pharma_list(user_id=current_user.id) )


@login_required
@views.route("/cow_liste", methods=["GET"])
def cow_liste():
    return render_template("cow_liste.html", user = current_user)


@login_required
@views.route("/user_setting", methods=["POST"])
def user_setting():
    try:
        # current_user : Users = current_user
        user_id = current_user.id
        dry_time = request.form["dry_time"]
        calving_preparation_time = request.form["calving_preparation_time"]

        UserUtils.set_user_setting(
            user_id=user_id, dry_time=int(dry_time), calving_preparation=int(calving_preparation_time) # type: ignore
        )

        CowUtils.reload_all_reproduction(user_id=user_id) # type: ignore

        return jsonify({"success": True, "message": "setting mis a jours."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@login_required
@views.route("/upload_cow/", methods=["POST"])
def upload_cows():
    file = request.files.get("file")
    if not file:
        return "Aucun fichier reçu", 400

    try:
        user_id = current_user.id
        # Lire le fichier Excel directement en mémoire
        df = pd.read_excel(BytesIO(file.read()), header=None)

        # Lire uniquement la première colonne (ex: ID de la vache)
        cow_ids = df.iloc[:, 0].dropna().unique()

        added, skipped = 0, 0
        for cow_id in cow_ids:
            try:
                CowUtils.add_cow(user_id=user_id, cow_id=int(cow_id), init_as_cow=True) # type: ignore
                added += 1
            except ValueError:
                skipped += 1

        return jsonify({"success": True,"message": f"{added} vache(s) ajoutée(s), {skipped} déjà existante(s)."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur de traitement : {e}"}), 500


@login_required
@views.route("/upload_calf/", methods=["POST"])
def upload_calfs():
    file = request.files.get("file")
    if not file:
        return "Aucun fichier reçu", 400

    try:
        user_id = current_user.id
        # Lire le fichier Excel directement en mémoire
        df = pd.read_excel(BytesIO(file.read()), header=None)

        # Lire uniquement la première colonne (ex: ID du veaux)
        calf_ids = df.iloc[:, 0].dropna().unique()

        added, skipped = 0, 0
        for calf_id in calf_ids:
            try:
                CowUtils.add_calf(user_id=user_id, calf_id=int(calf_id)) # type: ignore
                added += 1
            except ValueError:
                skipped += 1
                
        #TODO message a madofier
        return jsonify({"success": True,"message": f"{added} veaux(s) ajoutée(s), {skipped} déjà existante(s)."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur de traitement : {e}"}), 500

    
@login_required
@views.route("/init_stock", methods=["POST"])
def init_stock():
    #TODO Init par import odt/xls
    file = request.files.get("file")
    if not file:
        return "Aucun fichier reçu", 400

    try:
        user_id = current_user.id
        year = datetime.now().year -1
        remaining_stock: dict[str, int] = {}
        
        # Lire le fichier Excel directement en mémoire
        df = pd.read_excel(BytesIO(file.read()), header=None)

        # Lire uniquement la première colonne (ex: ID de la vache)
        medics = df.iloc[0:, 0].dropna().unique()
        print(medics)
        qt_medics = df.iloc[0:, 1].dropna().unique()
        print(qt_medics)
        units = df.iloc[0:, 2].to_list()
        print(units)
        

        added, skipped = 0, 0
        for medic,qt_medic,unit in zip(medics,qt_medics,units):
            try:
                remaining_stock[medic] = int(qt_medic)
                UserUtils.add_medic_in_pharma_list(user_id=user_id, medic=medic, mesur=unit) # type: ignore
                added += 1
            except ValueError:
                skipped += 1
        PharmacieUtils.upload_pharmacie_year(user_id=user_id, year=year, remaining_stock=remaining_stock) # type: ignore
        
        return jsonify({"success": True,"message": f"{added} médicament(s) ajouté(s), {skipped} déjà existant(s)."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur de traitement : {e}"}), 500
    # try:  
    #     # Récupère et parse la date
    #     year = request.form["prescription_date"]

    #     # Récupère les médicaments et quantités
    #     remaining_stock: dict[str, int] = {}
    #     for nb_care in range(get_pharma_len(current_user.id)):
    #         medic = request.form.get(f"medic_{nb_care+1}")
    #         quantite = request.form.get(f"medic_{nb_care+1}_nb")

    #         if medic and quantite:
    #             qte_int = int(quantite)
    #             if qte_int > 0:  # ignor les chaps vide
    #                 if medic in remaining_stock:
    #                     lg.error(
    #                         f"Quantité invalide pour medic_{nb_care+1}: {quantite}"
    #                     )
    #                     raise ValueError(f"Le médicament '{medic}' est en double.")
    #                 remaining_stock[medic] = qte_int

    #     if not remaining_stock:
    #         raise ValueError(
    #             "Veuillez renseigner au moins un médicament avec une quantité valide."
    #         )

    #     PharmacieUtils.upload_pharmacie_year(user_id=current_user.id, year=year, remaining_stock=remaining_stock) # type: ignore

    #     return jsonify(
    #         {"success": True, "message": "pharmacie initialiser avec succès."}
    #     )

    # except Exception as e:
    #     lg.error(f"Erreur pendant l’upload : {e}")
    #     return jsonify({"success": False, "message": f"Erreur : {str(e)}"})
