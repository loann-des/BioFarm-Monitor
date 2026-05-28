from datetime import datetime
from io import BytesIO
import logging as lg

from flask import (
    Blueprint,
    Response,
    jsonify,
    redirect,
    request,
    render_template,
    send_file,
    url_for
)

from flask_login import login_required, current_user  # type: ignore

from web_app.fonction import my_strftime, parse_date
from web_app.models.type_dict import Reproduction, Traitement

from ..connnected_user_web.connected_user import ConnectedUser

reproductionbp = Blueprint("reproduction", __name__)

current_user: ConnectedUser



@login_required
@reproductionbp.route("/reproduction/calendar", methods=["GET"])
def calendar():
    return render_template("calandar.html")


@login_required
@reproductionbp.route("/reproduction/get-reproduction", methods=["GET"])
def get_reproduction():
    try:
        cow_id = int(request.args["id"])
        if reproduction := current_user.cow_utils.get_waitting_reproduction(cow_id=cow_id):
            return jsonify({
                "success": True,
                "message": reproduction
            })
        else:
            return jsonify({
                "success": True,
                "message": None
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des stock: {e}"
        })


@login_required
@reproductionbp.route("/reproduction/get-all-reproductions", methods=["GET"])
def get_calving():
    try:
        reproductions = current_user.cow_utils.get_valid_reproduction()
        return jsonify({
            "success": True,
            "message": reproductions
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des reproductions : {e}"
        })


@login_required
@reproductionbp.route("/reproduction/get-all-reproductions-filter", methods=["GET"])
def get_all_reproductions_filter():
    try:
        idsearch = str(request.args.get("id_filter"))

        reproductions = {
            key: value
            for key, value in current_user.cow_utils.get_valid_reproduction().items()
            if idsearch in str(key)
        }
        
        return jsonify({
            "success": True,
            "message": reproductions
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des reproductions filtré : {e}"
        })


@login_required
@reproductionbp.route("/reproduction/ultrasound", methods=["POST"])
def ultrasound():
    try:
        cow_id = int(request.form["cow_id"])
        echo = request.form["echo_select"]
        if echo == "Vide":
            current_user.cow_utils.validated_ultrasound(
                cow_id=cow_id, ultrasound=False, date="")

        elif echo == "saillie":
            date = my_strftime(request.form["saillie"])
            current_user.cow_utils.add_insemination(
                cow_id=cow_id, insemination=date)
            current_user.cow_utils.validated_ultrasound(
                cow_id=cow_id, ultrasound=True, date=date)

        else:
            current_user.cow_utils.validated_ultrasound(
                cow_id=cow_id, ultrasound=True, date=echo)

        return jsonify({
            "success": True,
            "message": f"{cow_id}: echographie mise a jour avec succes"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la mise a jour de l'echographie: {e}"
        })


@login_required
@reproductionbp.route("/reproduction/calving", methods=["POST"])
def calving():
    try:
        mother_id = int(request.form["moter_id"])
        calf_id = int(request.form["calf_id"])
        calving_date = parse_date(request.form["calving_date"])
        calving_sexe = request.form["calving_sexe"] == "Femele"
        commentaire = request.form["commentaire"]
        current_user.cow_utils.validated_calving(cow_id=mother_id, calf_id=calf_id,
                                                 calving_date=calving_date, sexe=calving_sexe,
                                                 abortion=False, info=commentaire,)

        return jsonify({
            "success": True,
            "message": f"{mother_id}: velage enregistré avec succes,\n" +
            f"{calf_id} ajouter au veaux"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la mise a jour de l'echographie: {e}"
        })

@login_required
@reproductionbp.route("/reproduction/drying", methods=["POST"])
def drying():
    try:
        cow_id = request.form["id_cow"]
        current_user.cow_utils.validated_dry(int(cow_id))

        return jsonify({
            "success": True,
            "message": f"{cow_id}: trarissement mise a jour avec succes"
        })
        # TODO ms
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la mise a jour du trarissement: {e}"
        })

@login_required
@reproductionbp.route("/reproduction/calving_preparation", methods=["POST"])
def calving_preparation():
    try:
        cow_id = request.form["id_cow"]
        current_user.cow_utils.validated_calving_preparation(int(cow_id))

        return jsonify({
            "success": True,
            "message": f"{cow_id}: prépa vêlage mise a jour avec succes"
        })
        # TODO ms
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de la mise a jour de la prépa vêlage: {e}"
        })
