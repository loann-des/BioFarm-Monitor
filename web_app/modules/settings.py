import logging as lg
import pandas as pd

from datetime import datetime
from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask_login import login_required, current_user  # type: ignore
from io import BytesIO

from web_app.models.pharmacie import PharmacieUtils

from web_app.connnected_user_web.connected_user import ConnectedUser

from web_app.fonction import *
from web_app.models.cow import CowUtils
from web_app.models.user import UserUtils

settings = Blueprint("settings", __name__)

# TODO Metre en place les log
# TODO Metre en place historique commande pour retour
# TODO gestion de la reintroduction d'une vache


current_user: ConnectedUser


@login_required
@settings.route("/user_settings", methods=["POST"])
def user_settings():
    try:
        dry_time = request.form["dry_time"]
        calving_preparation_time = request.form["calving_preparation_time"]

        current_user.set_user_setting(
            dry_time=int(dry_time), calving_preparation=int(calving_preparation_time)
        )

        return jsonify(
            {"success": True,
             "message": "setting mis a jours.",
             "id": "user_settings"}
        )

    except Exception as e:
        lg.error(f"Erreur pendant l’upload : {e}")
        return jsonify(
            {"success": False,
             "message": f"Erreur : {str(e)}",
             "id": "user_settings"}
        )


# TODO securiser import de fichier.
# sur import de fichier verifier que c'est bien des entier et pas du BASH !!!
@login_required
@settings.route("/upload_cows/", methods=["POST"])
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
                CowUtils.add_cow(user_id=user_id, cow_id=int(
                    cow_id), init_as_cow=True)
                added += 1
            except ValueError:
                skipped += 1

        return jsonify(
            {
                "success": True,
                "message": f"{added} vache(s) ajoutée(s), {skipped} erreurs.",
                "id": "upload_cows",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False,
                 "message": f"Erreur de traitement : {e}",
                 "id": "upload_cows"},),
            500,
        )


@login_required
@settings.route("/upload_calfs/", methods=["POST"])
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
                CowUtils.add_calf(user_id=user_id, calf_id=int(calf_id))
                added += 1
            except ValueError:
                skipped += 1

        # TODO message a madofier
        return jsonify(
            {
                "success": True,
                "message": f"{added} veaux(s) ajoutée(s), {skipped} déjà existante(s).",
                "id": "upload_calfs",
            }
        )
    except Exception as e:
        return (
            jsonify({"success": False,
                     "message": f"Erreur de traitement : {e}",
                     "id": "upload_calfs"}),
            500,
        )


@login_required
@settings.route("/init_stock", methods=["POST"])
def init_stock():
    file = request.files.get("file")
    if not file:
        return "Aucun fichier reçu", 400

    try:
        user_id = current_user.id
        year = datetime.now().year
        remaining_stock: dict[str, int] = {}

        # Lire le fichier Excel directement en mémoire
        df = pd.read_excel(BytesIO(file.read()), header=None)

        # Lire uniquement la première colonne medics : nom du medicament
        medics = df.iloc[0:, 0].dropna().unique()
        # Lire uniquement la deuxième colonne qt_medics : quantite du medicament
        qt_medics = df.iloc[0:, 1].dropna().unique()
        # Lire uniquement la troisième colonne units : unitée du medicament
        units = df.iloc[0:, 2].to_list()

        added, skipped = 0, 0
        for medic, qt_medic, unit in zip(medics, qt_medics, units):
            try:
                remaining_stock[medic] = int(qt_medic)
                UserUtils.add_medic_in_pharma_list(
                    user_id=user_id, medic=medic, mesur=unit
                )
                added += 1
            except ValueError:
                skipped += 1
        PharmacieUtils.upload_pharmacie_year(
            user_id=user_id, year=year, remaining_stock=remaining_stock
        )

        return jsonify(
            {
                "success": True,
                "message": f"{added} médicament(s) ajouté(s), {skipped} déjà existant(s).",
                "id": "init_stock",
            }
        )
    except Exception as e:
        return (
            jsonify(
                {"success": False,
                 "message": f"Erreur de traitement : {e}",
                 "id": "init_stock"},),
            500,
        )
