from typing import List, Tuple
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from sqlalchemy import Column, Integer, PickleType, String, Enum, DATE, URL, LargeBinary
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime ,date
import logging as lg
import enum

from .views import app

# Create database connection object
db = SQLAlchemy(app)

date_now = datetime.now()

class Cow(db.Model):
    id = Column(Integer, primary_key=True) #numero Vache
    traitement: List[Tuple[date, str, str]] #liste de (date de traitement, traitement, info complementaire)
    traitement = Column(MutableList.as_mutable(PickleType),
                        default=list,
                        nullable=False
                        )
    traitement: List[Tuple[str, date]]#liste de (date de l'annotation, annotation general)
    info = Column(MutableList.as_mutable(PickleType),
                    default=list,
                    nullable=False
                    )

    def __init__(self, id, traitement):
        self.id = id
        self.traitement = traitement

class Prescription(db.Model):
    id = Column(Integer, primary_key=True) #id Prescription
    date = Column(DATE) # date de la Prescription
    traitement: List[Tuple[str, int]]#liste de (medicament, nb medicament)
    traitement = Column(MutableList.as_mutable(PickleType),
                        default=list,
                        nullable=False
                        )

    



def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    lg.warning("Database initialized!")


def upload_cow(id : int, traitement : List[Tuple[str, date, str]]) -> None :
    new_cow = Cow(
        id=id,traitement=traitement if traitement is not None else []
    )
    db.session.add(new_cow)
    db.session.commit()
    
def update_care(id : int, care : tuple[str,date]) -> int :
    # Récupérer la vache depuis la BDD
    cow :Cow = Cow.query.get(id)
    if not cow:
        lg.error(f"Cow with id {id} not found.")
        return 0  # ou lever une exception selon ta gestion d'erreur
    
    # Ajouter le traitement à la liste
    cow.traitement.append(care)
    
    # Commit les changements
    db.session.commit()
    lg.info(f"Traitement ajouté à la vache {id}: {care}")
    return 3 - len(cow.traitement) #return le nombre de traitement restent autoriser

def remove_cow(id : int) -> None :
    cow = Cow.query.get(id)
    if cow :
        db.session.delete(cow)
        db.session.commit()
        lg.info(f"La vache {id} a été supprimée.")
    else:
        lg.warning(f"Aucune vache trouvée avec l'id {id}.")