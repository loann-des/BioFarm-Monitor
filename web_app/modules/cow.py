import json
import logging as lg

from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    render_template,
    url_for
)

from flask_login import login_required, current_user  # type: ignore

from web_app.fonction import my_strftime, parse_date, reload_reproduction_with
from web_app.models.type_dict import Reproduction, Traitement  # type: ignore

from ..connnected_user_web.connected_user import ConnectedUser
from web_app.models.cow import CowUtils

cowbp = Blueprint("cow", __name__)

current_user: ConnectedUser


@cowbp.before_request
def check_authentication():
    if current_user.is_anonymous:
        return redirect(url_for("auth.login"))


@login_required
@cowbp.route("/cow/<int:cow_id>", methods=["GET"])
def display_cow(cow_id):
    cow = current_user.cow_utils.get_cow(cow_id)
    return render_template("cow.html", cow=cow, medic_list=current_user.medic_list)


@login_required
@cowbp.route("/cow/remove", methods=["POST"])
def remove_cow():
    cow_id = int(request.form["id"])

    try:
        current_user.cow_utils.remove_cow(cow_id)
        return jsonify({
            "success": True,
            "message": f"La sortie de la vache {cow_id} a bien été enregistrée"
        })
    except Exception as e:
        lg.error(f"Erreur lors de la sortie de la vache {cow_id}: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de la sortie de la vache {cow_id}"
        })


@login_required
@cowbp.route("/cow/change", methods=["POST"])
def change():
    try:
        cow_id = int(request.form["cow_id"])

        if request.form["name"]:
            current_user.cow_utils.update_cow(
                cow_id, name=request.form["name"])  # type: ignore

        if request.form["birthdate"]:
            current_user.cow_utils.update_cow(
                cow_id=cow_id,
                born_date=
                parse_date(request.form["birthdate"])) # type: ignore

        return jsonify({
            "success": True,
            "message": "Vache modifiée"
        })
    except Exception as e:
        lg.error(f"Erreur lors de la modification de la vache: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de la modification de la vache: {e}"
        })


@login_required
@cowbp.route("/cow/add-insemination", methods=["POST"])
def add_insemination():
    # TODO limiter a une reproduction en cours
    try:
        cow_id = int(request.form["cow_id"])
        inseminsation_date = my_strftime(request.form["date"])

        if inseminsation_date:
            current_user.cow_utils.add_insemination(cow_id, inseminsation_date)

            return jsonify({
                "success": True,
                "message": "Insémination ajoutée à la vache"})
        else:
            return jsonify({
                "success": False,
                "message": "Date manquante pour l'insémination"
            })
    except Exception as e:
        lg.error(f"Erreur lors de l'ajout de la reproduction: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de l'ajout de la reproduction: {e}"
        })


@login_required
@cowbp.route("/cow/add_care", methods=["POST"])
def add_care():
    try:
        cow_id: int = int(request.form["cow_id"])
        care_date: str = my_strftime(request.form["date"])

        medicaments_list = request.form.getlist("medication")
        quantites = [int(q) for q in request.form.getlist("dose")]
        medicaments = dict(zip(medicaments_list, quantites))

        note = request.form["note"]

        traitement: Traitement = Traitement(
            date_traitement=care_date, medicaments=medicaments, annotation=note, id=0)
        current_user.cow_utils.add_cow_care(cow_id, traitement)

        return jsonify({
            "success": True,
            "message": f"Traitement ajouté à la vache "
            #TODO ajouter les traitement restant dans le message
            })
    except Exception as e:
        lg.error(f"Erreur lors de l'ajout du traitement: {e}")

        return jsonify({
            "success": False,
            "message": f"Erreur lors de l'ajout du traitement: {e}"
        })


@login_required
@cowbp.route("/cow/remove_reproduction", methods=["POST"])
def remove_reproduction():
    try:
        cow_id: int = int(request.form["cow_id"])
        index: int = int(request.form["index"])
        print(index)
        current_user.cow_utils.delete_cow_reproduction(cow_id, index)
        return jsonify({
            "success": True,
            "message": "Reproduction supprimée"
        })
    except Exception as e:
        lg.error(f"Erreur lors de la suppression de la reproduction: {e}")
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la suppression de la reproduction: {e}"
        })


@login_required
@cowbp.route("/cow/modify_reproduction", methods=["POST"])
def modify_reproduction():
    try:
        cow_id: int = int(request.form["cow_id"])
        index: int = int(request.form["index"])
        isneminaton = [my_strftime(
            isemination_date) for isemination_date in request.form.getlist("insemination")]
        cow = current_user.cow_utils.get_cow(cow_id)
        if not cow:
            return jsonify({
                "success": False,
                "message": "Vache non trouvée"
            })
        repro : Reproduction = cow.reproduction[index]
        new_repro = Reproduction(
            insemination=isneminaton,
            ultrasound=bool(request.form["ultrasound"]) if request.form["ultrasound"] != "None" else None,
            dry=repro["dry"],
            dry_status=bool(request.form["dry"]),
            calving_preparation=repro["calving_preparation"],
            calving_preparation_status=bool(request.form["prep"]),
            calving_date=repro["calving_date"],
            calving=bool(request.form["calving"]),
            abortion=bool(request.form["abortion"]),
            reproduction_details=request.form["reproduction_details"]
        )
        reproduction = reload_reproduction_with(repro, new_repro, current_user.setting)
        current_user.cow_utils.update_cow_reproduction(cow_id, index, reproduction)
        return jsonify({
            "success": True,
            "message": "Reproduction modifiée"
        })
    except Exception as e:
        lg.error(f"Erreur lors de la modification de la reproduction: {e}")
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la modification de la reproduction: {e}"
        })


@login_required
@cowbp.route("/cow/remove_care", methods=["POST"])
def remove_care():
    # TODO remove_care
    return jsonify({
        "success": False,
        "message": "Not implemented yet"
    })


@login_required
@cowbp.route("/cow/modify_care", methods=["POST"])
def modify_care():
    # TODO: Implement care modification logic
    return jsonify({
        "success": False,
        "message": "Not implemented yet"
    })


@login_required
@cowbp.route("/cow/get-cares", methods=["GET"])
def get_cares():
    cow_id = request.args.get("cow_id")
    if not cow_id:
        return jsonify({
            "success": False,
            "message": "Argument cow_id is missing"
        })
    else:
        cow_id = int(cow_id)

    try:
        if cow := current_user.cow_utils.get_cow(cow_id):
            cow_cares = cow.cow_cares
            cow_cares.reverse()
            return jsonify({
                "success": True,
                "message": cow_cares
            })
        else:
            return jsonify({
                "success": False,
                "message": "Vache non trouvée"
            })

    except Exception as e:
        lg.error(f"Failed to get cow cares: {e}")

        return jsonify({
            "success": False,
            "message": f"Failed to get cow cares: {e}"
        })


@login_required
@cowbp.route("/cow/get-reproductions", methods=["GET"])
def get_reproductions():
    cow_id = request.args.get("cow_id")
    if not cow_id:
        return jsonify({
            "success": False,
            "message": "Argument cow_id is missing"
        })
    else:
        cow_id = int(cow_id)

    try:
        if cow := current_user.cow_utils.get_cow(cow_id):
            cow_reproductions = cow.reproduction
            cow_reproductions.reverse()
            return jsonify({
                "success": True,
                "message": cow_reproductions
            })
        else:
            return jsonify({
                "success": False,
                "message": "Vache non trouvée"
            })
    except Exception as e:
        lg.error(f"Failed to get cow reproductions: {e}")

        return jsonify({
            "success": False,
            "message": f"Failed to get cow reproductions: {e}"
        })
