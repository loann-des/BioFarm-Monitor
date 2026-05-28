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

calandarbp = Blueprint("calandar", __name__)

current_user: ConnectedUser


@login_required
@calandarbp.route("/reproduction/calandar/export-calendar", methods=["GET"])
def export_calendar():
    try:
        file_bytes = current_user.cow_utils.export_calandar()
        return send_file(
            file_bytes,
            mimetype="text/calendar",
            as_attachment=True,
            download_name="calendar.ics"
        )
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors du Telecargement: {e}"
        })


@login_required
@calandarbp.route("/reproduction/calandar/calendar-data", methods=["GET"])
def get_reproduction():
    try:
        events = current_user.cow_utils.reproduction_fullcalendar()
        if events:
            return jsonify({
                "success": True,
                "message": events
            })
        else:
            return jsonify({
                "success": True,
                "message": None
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur lors de recuperation des evenements: {e}"
        })
