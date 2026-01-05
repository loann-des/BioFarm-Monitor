import os
import logging as lg

class HTTP304Filter(lg.Filter):
    def filter(self, record):
        # Ignore les logs contenant " 304 " (code HTTP 304)
        return " 304 " not in record.getMessage()

class config :

    # Configuration de la session
    PERMANENT_SESSION_LIFETIME = 60*60  # Durée de vie de la session en secondes (1 minute)
   
    # Configuration du logging pour toute l'application
    lg.basicConfig(
        filename='app.log',  # Nom du fichier log
        level=lg.INFO,       # Niveau de log (INFO, WARNING, ERROR, etc.)
        format='%(asctime)s %(levelname)s %(message)s'
    )
    for handler in lg.getLogger().handlers:
        handler.addFilter(HTTP304Filter())

    SECRET_KEY = '#d#JCqTTW\nilK\\7m\x0bp#\tj~#H'

    APP_G_ID = 1200420960103822

    # Database initialization
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    # Configuration Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

config = config() # type: ignore