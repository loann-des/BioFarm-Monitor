from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for
)

from flask_login import login_required, current_user # type: ignore

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
    cow = CowUtils.get_cow(current_user.id, cow_id)

    return render_template("cow.html", cow=cow)
