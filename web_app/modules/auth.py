from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from ..models.user import UserUtils, Users
from ..connected_user import ConnectedUser
from .. import db

nb_user : int
nb_connected_user : int

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/login', methods=['POST'])
def login_post():
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))
    remember = bool(request.form.get('remember'))

    user : Users = UserUtils.get_user_by_email(email=email)

    if not user or not check_password_hash(user.password, password): # type: ignore
        return jsonify({"success": False, "message": f"Erreur : {"incorect password" if user else "mail inconnue"}"})

    if not login_user(ConnectedUser(user=user), remember=remember, force=True):
        return jsonify({"success": False, "message": "Erreur lors de la connexion."})
    return redirect(url_for('views.index'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    if Users.query.filter_by(email=email).first():
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = Users(email=email, name=name, password=generate_password_hash(password)) # type: ignore
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
