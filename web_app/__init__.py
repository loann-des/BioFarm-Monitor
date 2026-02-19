from datetime import timedelta
from flask import Flask, g, redirect, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, logout_user


# Initialize SQLAlchemy instance (outside create_app for import access)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.config")

    # Initialize extensions with app
    db.init_app(app)

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # type: ignore
    login_manager.session_protection = "strong"
    login_manager.init_app(app)

    # User loader function for Flask-Login
    from .connected_user import ConnectedUser

    @login_manager.user_loader
    def load_user(user_id:int):
        return ConnectedUser(user_id=user_id)


    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=60) #TODO lifetime session
        session.modified = True


    # Register blueprints
    from .modul.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .modul.views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    from .modul.pharmacie import pharma as pharma_blueprint
    app.register_blueprint(pharma_blueprint)

    from .modul.reproduction import repro as repro_blueprint
    app.register_blueprint(repro_blueprint)

    from .modul.cow_liste import cow_liste as cow_liste_blueprint
    app.register_blueprint(cow_liste_blueprint)


    # Jinja2 global functions
    from .fonction import format_bool_fr, date_to_str
    from .models import CowUtils
    app.jinja_env.globals.update(enumerate=enumerate)
    app.jinja_env.globals.update(get_all_cows=CowUtils.get_all_cows)
    app.jinja_env.globals.update(date_to_str=date_to_str)
    app.jinja_env.globals.update(format_bool_fr=format_bool_fr)

    return app



app = create_app()

@app.cli.command("init_db")
def init_db():
    from .models import init_db
    init_db()
