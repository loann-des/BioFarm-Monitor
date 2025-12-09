from datetime import timedelta
from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user


# Initialize SQLAlchemy instance (outside create_app for import access)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.config")

    # Initialize extensions with app
    db.init_app(app)

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager
    login_manager.init_app(app)

    # User loader function for Flask-Login
    from .models import Users
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=1)
        session.modified = True
        # g.user = current_user

    # Register blueprints
    from .modul.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .modul.views import views as views_blueprint
    app.register_blueprint(views_blueprint)

    from .modul.pharmacie import pharma as pharma_blueprint
    app.register_blueprint(pharma_blueprint)

    from .modul.reproduction import repro as repro_blueprint
    app.register_blueprint(repro_blueprint)

    # Jinja2 global functions
    from .fonction import get_pharma_list, get_pharma_len, get_hystory_pharmacie, strftime, format_bool_fr
    from .models import CowUntils
    app.jinja_env.globals.update(enumerate=enumerate)
    app.jinja_env.globals.update(get_pharma_list=get_pharma_list)
    app.jinja_env.globals.update(get_pharma_len=get_pharma_len)
    app.jinja_env.globals.update(get_hystory_pharmacie=get_hystory_pharmacie)
    app.jinja_env.globals.update(get_all_cows=CowUntils.get_all_cows)
    app.jinja_env.globals.update(strftime=strftime)
    app.jinja_env.globals.update(format_bool_fr=format_bool_fr)

    return app



app = create_app()

@app.cli.command("init_db")
def init_db():
    from .models import init_db
    init_db()




