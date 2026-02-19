from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for
)

from flask_login import login_required, current_user

from ..connected_user import ConnectedUser
from ..models import CowUtils

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
