from datetime import datetime
from io import BytesIO
import pandas as pd
from time import strftime
from flask import (
    Flask,
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
import logging as lg
from flask_login import LoginManager, login_required, current_user

views = Blueprint('views', __name__)

# app = Flask(__name__)
# app.config.from_object("config.config")

# Configure Flask-Login
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
# login_manager.init_app(app)


from .fonction import *
from .models import CowUntils, PrescriptionUntils, PharmacieUtils, UserUtils

# TODO edit
# TODO gestion des log
# TODO historique commande
# TODO reintroduction d'une vache


# User loader function for Flask-Login
# @login_manager.user_loader
# def load_user(user_id):
#     return UserUtils.get_user(user_id=user_id)

# # Register blueprints
# from .auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint)

# root

@views.route("/", methods=["GET","POST"])
@login_required
def index():
    return render_template("index.html",user=current_user)


@views.route("/reproduction", methods=["GET"])
def reproduction():
    return render_template("reproduction.html")


@views.route("/pharmacie", methods=["GET"])
def pharmacie():
    return render_template("pharmacie.html")


@views.route("/cow_liste", methods=["GET"])
def cow_liste():
    return render_template("cow_liste.html")


@views.route("/user_setting", methods=["POST"])
def user_setting():
    try:
        user_id = 1  # TODO get user id from session
        dry_time = request.form["dry_time"]
        calving_preparation_time = request.form["calving_preparation_time"]

        UserUtils.set_user_setting(
            user_id=user_id, dry_time=dry_time, calving_preparation=calving_preparation_time
        ) 
        
        CowUntils.reload_all_reproduction(user_id=user_id)

        return jsonify({"success": True, "message": "setting mis a jours."})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


# Pharmacie form


@views.route("/update_care", methods=["POST"])
def update_care():
    # TODO valider traitemment seulement si pas de bug (dernier opération)
    def extract_cares(form : dict, pharma_len : int):
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

    def extract_care_date_and_info(form : dict):
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

        remain_care = CowUntils.add_cow_care(id=id_cow, cow_care=care)

        success_message = f"il reste : {remain_care[0]} traitement autoriser en bio jusque'au {remain_care[1]} pour {id_cow}."
        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@views.route("/add_prescription", methods=["POST"])
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


@views.route("/add_dlc_left", methods=["POST"])
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


@views.route("/add_medic_in_pharma_list", methods=["POST"])
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


@views.route("/init_stock", methods=["POST"])
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


@views.route("/get_stock", methods=["GET"])
def get_stock():
    try:
        year = datetime.now().year  #on récupère l'année 
        stock_data = remaining_pharmacie_stock(year)
        return jsonify({"success": True, "stock": stock_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@views.route("/stock_details", methods=["GET"])
def stock_details():
    return render_template("stock_details.html")


@views.route("/download", methods=["GET", "POST"])
def download():
    lg.info("export-stock")
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


@views.route("/download_remaining_care", methods=["GET", "POST"])
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

# Reproduction form
@views.route("/upload_cow/", methods=["GET", "POST"])
def upload_cows():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return "Aucun fichier reçu", 400

        try:
            user_id = 1  # TODO get user id from session
            # Lire le fichier Excel directement en mémoire
            df = pd.read_excel(BytesIO(file.read()))

            # Lire uniquement la première colonne (ex: ID de la vache)
            cow_ids = df.iloc[:, 0].dropna().unique()

            added, skipped = 0, 0
            for cow_id in cow_ids:
                try:
                    CowUntils.add_cow(user_id=user_id, cow_id=int(cow_id))
                    added += 1
                except ValueError:
                    skipped += 1

            return jsonify({"success": True,"message": f"{added} vache(s) ajoutée(s), {skipped} déjà existante(s)."})
        except Exception as e:
            return jsonify({"success": False, "message": f"Erreur de traitement : {e}"}), 500

@views.route("/add_cow", methods=["POST"])
def add_cow():
    # TODO gestion veaux upload_cow
    try:
        user_id = 1  # TODO get user id from session
        # Récupération des données du formulaire
        cow_id = int(request.form["id"])

        lg.info(f"Adding new cow {cow_id}...")

        CowUntils.add_cow(user_id=user_id, cow_id=int(cow_id))

        return jsonify(
            {"success": True, "message": f"{cow_id} a été ajoutée avec succès !"}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


@views.route("/remove_cow", methods=["POST"])
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


@views.route("/insemination", methods=["POST"])
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


@views.route("/ultrasound", methods=["POST"])
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


@views.route("/show_dry")
def show_dry():
    #TODO valider dry
    try:
        dry_data = get_all_dry_date()
        return jsonify({"success": True, "dry": dry_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@views.route("/validate_dry", methods=["POST"])
def validate_dry():
    data = request.get_json()
    cow_id = data.get("cow_id")

    if not cow_id:
        return jsonify({"success": False, "message": "Aucune vache spécifiée."}), 400

    try:
        CowUntils.validated_dry(cow_id=cow_id)

        return jsonify({"success": True, "message": f"Tarissement validé pour {cow_id}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@views.route("/show_calving_preparation")
def show_calving_preparation():
    #TODO valider calving preparation
    try:
        calving_preparation = get_all_calving_preparation_date()
        return jsonify({"success": True, "calving_preparation": calving_preparation})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@views.route("/show_calving_date")
def show_calving_date():
    try:
        calving_data = get_all_calving_date()
        return jsonify({"success": True, "calving": calving_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@views.route("/upload_calf", methods=["POST"])
def upload_calf():
    # TODO gestion veaux upload_cow
    try:
        # Récupération des données du formulaire
        borning = request.form["borning"]
        mother_id = request.form["mother_id"]
        calf_id = request.form["calf_id"]
        calving_date = request.form["calving_date"]
        if borning == "abortion":
            CowUntils.validated_calving(cow_id=mother_id, abortion=True)
            success_message = f"avortement de {mother_id} rensegné, courage"

        elif calf_id and calving_date:
            lg.info(f"Adding new calf {calf_id}...")
            CowUntils.validated_calving(cow_id=mother_id, abortion=False)
            calving_date = datetime.strptime(calving_date, "%Y-%m-%d").date()
            CowUntils.add_calf(calf_id=calf_id, born_date=calving_date)
            success_message = f"naissance de {calf_id} confirmé"
        else:
            raise ValueError('Renségner "Numéro Veau" et  "Date de velage"')

        return jsonify({"success": True, "message": success_message})

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


# END  Reproduction form

# cow_liste form


@views.route("/cow_liste/view_cow/<int:cow_id>", methods=["GET", "POST"])
def view_cow(cow_id):
    if cow := CowUntils.get_cow(cow_id=cow_id):
        print("🐄 Vache récupérée :", cow)
        return render_template("cow_details.html", cow=cow)
    else:
        return "Vache introuvable", 404


@views.route("/cow_liste/edit_cow/<int:cow_id>", methods=["GET", "POST"])
def edit_cow(cow_id):
    return render_template("cow_edit.html", cow=CowUntils.get_cow(cow_id=cow_id))


@views.route("/cow_liste/suppress_cow/<int:cow_id>", methods=["POST"])
def suppress_cow(cow_id):
    # TODO Ajout ms confirmation avant suppression
    lg.info(f"Suppression de la vache {cow_id}...")
    try:
        CowUntils.suppress_cow(cow_id=cow_id)
        return jsonify({"success": True, "message": f"Vache {cow_id} supprimée."})
    except Exception as e:
        lg.error(f"Erreur pendant la suppression de la vache {cow_id}: {e}")
        return jsonify({"success": False, "message": f"Erreur : {str(e)}"})


# END cow_liste form


# cow_edit form


@views.route("/update_cow_details/<int:cow_id>", methods=["POST"])
def update_cow_details(cow_id):
    # Récupération des données du formulaire
    in_farm = bool(request.form.get("in_farm"))
    born_date_str = request.form.get("born_date")
    born_date = datetime.strptime(born_date_str, "%Y-%m-%d").date()
        
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
        CowUntils.update_cow(cow_id, **update_data)
        flash("Vache mise à jour avec succès.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("edit_cow", cow_id=cow_id))

@views.route("/update_cow_care/<int:cow_id>/<int:care_index>", methods=["POST"])
def update_cow_care(cow_id, care_index):

    # Récupération des données du formulaire
    date_str = request.form.get("care_date")
    new_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    new_info = request.form.get("care_info", "")

    # Récupération des médicaments
    meds = {}
    i = 1
    while med := request.form.get(f"medic_{i}"):
        if qty := request.form.get(f"medic_{i}_nb"):
            meds[med] = int(qty)
        i += 1

    CowUntils.update_cow_care(
        cow_id=cow_id, care_index=care_index, new_care=(new_date, meds, new_info)
    )

    flash("Soin modifié avec succès", "success")
    return redirect(url_for("edit_cow", cow_id=cow_id))  # ou autre vue

@views.route('/delete_cow_care/<int:cow_id>/<int:care_index>', methods=['POST'])
def delete_cow_care(cow_id, care_index):
    try:
        CowUntils.delete_cow_care(cow_id=cow_id, care_index=care_index)
        flash("Soin supprimé.")
    except IndexError:
        flash("Soin introuvable.")
    return redirect(url_for('edit_cow', cow_id=cow_id))

@views.route("/update_cow_reproduction/<int:cow_id>/<int:repro_index>", methods=["POST"])
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
        CowUntils.update_cow_reproduction(
            cow_id=cow_id, repro_index=repro_index, new_repro=(new_repro, info)
        )

    except (ValueError, KeyError) as e:
        flash(f"Erreur lors de la mise à jour: {e}", "error")
    except Exception as e:
        views.logger.exception("Unexpected error during cow reproduction update")
        raise

    return redirect(url_for("cow_details", cow_id=cow_id))

@views.route('/delete_cow_reproduction/<int:cow_id>/<int:repro_index>', methods=['POST'])
def delete_cow_reproduction(cow_id, repro_index):
    try:
        CowUntils.delete_cow_reproduction(cow_id=cow_id, repro_index=repro_index)
        flash("Reproduction supprimée.")
    except IndexError:
        flash("Reproduction introuvable.")
    return redirect(url_for('edit_cow', cow_id=cow_id))

# END cow_edit form

# Jinja2 global functions

# views.jinja_env.globals.update(enumerate=enumerate)
# views.jinja_env.globals.update(get_pharma_list=get_pharma_list)
# views.jinja_env.globals.update(get_pharma_len=get_pharma_len)
# views.jinja_env.globals.update(get_hystory_pharmacie=get_hystory_pharmacie)
# views.jinja_env.globals.update(get_all_cows=CowUntils.get_all_cows)
# views.jinja_env.globals.update(strftime=strftime)
# views.jinja_env.globals.update(format_bool_fr=format_bool_fr)

