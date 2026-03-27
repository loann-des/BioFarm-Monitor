from werkzeug.security import generate_password_hash
import logging as lg

from web_app.models.user import UserUtils


from .. import db

def init_db() -> None:
    """Initialise la base de données. Pour ce faire, supprime toutes les tables,
    les re-créée et les remplit avec les entrées par défaut.

    Cette fonction réinitialise la base de données, ajoute des utilisateurs,
    enregistre les changements (commit) et marque dans le journal que la base
    de données a été réinitialisée.
    """
    db.drop_all()
    db.create_all()
    UserUtils.add_user(email="adm@mail.com",
                       password=generate_password_hash(password="adm"))
    UserUtils.add_user(email="adm2@mail.com",
                       password=generate_password_hash(password="adm"))
    db.session.commit()
    lg.warning("Database initialized!")
    
def init_db_test() -> None:
    db.drop_all()
    db.create_all()
    lg.warning("Database initialized!")