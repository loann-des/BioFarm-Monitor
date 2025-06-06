from typing import List, Optional, Tuple, TypedDict
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from sqlalchemy import Column, Integer, PickleType, String, Enum, DATE, URL, LargeBinary, Boolean, JSON
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime ,date
import logging as lg
import enum

from .views import app

# Create database connection object
db = SQLAlchemy(app)

class CareItem(TypedDict):
    medicament: str
    quantite: Optional[int]

class Cow(db.Model):
    id = Column(Integer, primary_key=True) #numero Vache
    traitement: List[Tuple[date, str, str]] #liste de (date de traitement, traitement, info complementaire)
    traitement = Column(MutableList.as_mutable(PickleType),
                        default=list,
                        nullable=False 
                        )
    info: List[Tuple[str, date]]#liste de (date de l'annotation, annotation general)
    info = Column(MutableList.as_mutable(PickleType),
                    default=list,
                    nullable=False
                    )
    in_farm = Column(Boolean)# faux si vache sortie expoitation

    def __init__(self, id : int , traitement : list[tuple[date, str, str]], in_farm: bool):
        self.id = id
        self.traitement = traitement
        self.in_farm = in_farm

class Prescription(db.Model):
    id = Column(Integer, primary_key=True) #id Prescription
    date = Column(DATE) # date de la Prescription
    
    # Traitement stocké au format JSON en base
    traitement: List[CareItem]
    traitement = Column(MutableList.as_mutable(JSON), default=list, nullable=False)

    def __init__(self, date : DATE, traitement : list[CareItem]):
        self.date = date
        self.traitement = traitement
        
    
def init_db():
    db.drop_all()
    db.create_all()
    db.session.add(Prescription(date=None,traitement=[]))
    db.session.commit()
    lg.warning("Database initialized!")


def upload_cow(id : int, traitement : List[Tuple[str, date, str]]) -> None :
    #TODO Getion doublon
    new_cow = Cow(
        id=id,traitement=traitement if traitement is not None else [], in_farm=True
    )
    db.session.add(new_cow)
    db.session.commit()
    
    
def update_care(id : int, care : tuple[str,date]) -> tuple[int, date]:
    from .fonction import nb_cares_years

    # Récupérer la vache depuis la BDD
    cow :Cow
    if cow := Cow.query.get(id):
        return add_care(cow, care, id, nb_cares_years(cow))
    lg.error(f"Cow with id {id} not found.")
    return (0,None)  # ou lever une exception selon ta gestion d'erreur


def add_care(cow : Cow , care: Tuple[str,date,str], id : int, nb_cares_years : int):
    # Ajouter le traitement à la liste
    cow.traitement.append(care)

    # Commit les changements
    db.session.commit()
    lg.info(f"Traitement ajouté à la vache {id}: {care}")

    nb_care = nb_cares_years(cow=cow) # nombre de traitement dans l'année glissante
    remaining_care = (3 - nb_care)  # traitement restant dans l'année glissante
    new_available_care = cow.traitement[-nb_care][1] # date de disponibilité de nouveux traitement
    
    return remaining_care, new_available_care


def get_care_by_id(id : int) -> Tuple[str, date, str] :
    # Récupérer la vache depuis la BDD
    cow: Cow
    if cow := Cow.query.get(id) :
        return cow.traitement
    lg.error(f"Cow with id {id} not found.")
    return None  # ou lever une exception selon ta gestion d'erreur
   

def remove_cow(id : int) -> None:
    cow :Cow
    if cow := Cow.query.get(id):
        cow.in_farm = False
        db.session.commit()
        lg.info(f"La vache {id} a été supprimée.")
    else:
        lg.warning(f"Aucune vache trouvée avec l'id {id}.")
        

def add_prescription(date : date, care_items : List[dict]):
    prescription = Prescription(date=date,traitement=care_items)
    db.session.add(prescription)
    db.session.commit()
    
    
def add_medic_in_pharma_liste(medic : str):
    pharma_liste : Prescription = Prescription.query.get(1)
    pharma_liste.traitement.append({
        "medicament": f"{medic}",
        "quantite": None
    })
    db.session.commit()
    care_item : CareItem
    for care_item in get_pharma_liste():
        lg.warning(f"{care_item['medicament']}")

def get_pharma_liste()-> List[CareItem] :
    pharma_liste : Prescription = Prescription.query.get(1)
    return [
        CareItem(medicament=item["medicament"], quantite=item.get("quantite"))
        for item in pharma_liste.traitement
    ]