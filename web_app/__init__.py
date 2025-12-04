from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# from .views import app
# from .models import db
# from .fonction import *

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
    login_manager.init_app(app)
    
    # User loader function for Flask-Login
    from .models import Users
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .views import views as views_blueprint
    app.register_blueprint(views_blueprint)
    
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
    # models.init_db()
    
# @app.cli.command("get_all")
# def get_all():
    
#     print(fonction.get_AllArticle())
