from typing import List, Optional, Tuple, TypedDict
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, PickleType, DATE, Boolean, JSON, extract
from sqlalchemy.ext.mutable import MutableList, MutableDict
from datetime import date, timedelta
import logging as lg

from .views import app

# Create database connection object
db = SQLAlchemy(app)


class Reproduction(TypedDict):
    insemination: date
    ultrasound : Optional[bool]
    dry : date
    calving_preparation: date
    calving_date : date
    calving : bool
    
class Setting(TypedDict):
    dry_time : int #Temps de tarrisement (en jour)
    calving_preparation_time: int  #Temps de prepa vellage (en jour)
    
class Cow(db.Model):
    id = Column(Integer, primary_key=True)  # numero Vache
    # liste de (date de traitement, traitement, info complementaire)
    cow_cares = Column(MutableList.as_mutable(PickleType), default=list, nullable=False)
    # liste de (date de l'annotation, annotation general)
    info = Column(MutableList.as_mutable(PickleType), default=list, nullable=False)
    in_farm = Column(Boolean)  # faux si vache sortie expoitation
    born_date = Column(DATE)
    reproduction = Column(MutableList.as_mutable(PickleType), default=list, nullable=False)
    
    
    def __init__(
        self,
        id: int,
        cow_cares: list[tuple[date, dict[str, int], str]],
        in_farm: bool,
        born_date: date,
        reproduction : list[tuple[Reproduction, str]]
    ):
        self.id = id
        self.cow_cares = cow_cares
        self.in_farm = in_farm
        self.born_date = born_date
        self.reproduction = reproduction


class Prescription(db.Model):
    id = Column(Integer, primary_key=True)  # id Prescription
    date = Column(DATE)  # date de la Prescription

    # Traitement stocké au format JSON en base
    care = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)

    dlc_left = Column(Boolean)

    def __init__(self, date: DATE, care: dict[str, int], dlc_left: bool):
        self.date = date
        self.care = care
        self.dlc_left = dlc_left


class Pharmacie(db.Model):
    year_id = Column(Integer, primary_key=True)

    total_used = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_used_calf = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_out_dlc = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_out = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    remaining_stock = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)

    def __init__(
        self,
        year_id: int,
        total_used: dict[str:int],
        total_used_calf: dict[str:int],
        total_out_dlc: dict[str:int],
        total_out: dict[str:int],
        remaining_stock: dict[str:int],
    ):
        self.year_id = year_id
        self.total_used = total_used
        self.total_used_calf = total_used_calf
        self.total_out_dlc = total_out_dlc
        self.total_out = total_out
        self.remaining_stock = remaining_stock


class Users(db.Model):
    id = Column(Integer, primary_key=True)  # numero utilisateur
    setting = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False) #setting utilisateur
    
    def __init__(self,setting : Setting):
        self.setting = setting

def init_db() -> None:
    db.drop_all()
    db.create_all()
    db.session.add(Prescription(date=None, care={}, dlc_left=True))
    db.session.commit()
    lg.warning("Database initialized!")


# COW FONCTION


def upload_cow(id: int, born_date) -> None:
    """Adds a new cow to the database if it does not already exist.

    If a cow with the given ID is not present, it is created and added to the database. Otherwise, an error is logged.

    Args:
        id (int): The unique identifier for the cow to be uploaded.

    Returns:
        None
    """
    if not Cow.query.get(id):
        new_cow = Cow(id=id, cow_cares=[], in_farm=True, born_date=born_date, reproduction=[])
        db.session.add(new_cow)
        db.session.commit()
        lg.info(f"{id} : upload in database")
    else:
        lg.error(f"{id} : already in database")


def update_care(
    id: int, cow_care: Tuple[date, dict, str]
) -> Optional[tuple[int, date]]:
    """Updates the care record for a cow with the specified ID.

    If the cow exists, the care is added and a tuple with the number of remaining cares and the date of new available care. If the cow does not exist, an error is logged and None is returned.

    Args:
        id (int): The unique identifier for the cow.
        cow_cares (Tuple[date, dict, str]): The care information to add.

    Returns:
        Optional[tuple[int, date]]: The number of remaining cares and the date of new available care, or None if the cow is not found.
    """
    from .fonction import nb_cares_years

    # Récupérer la vache depuis la BDD
    cow: Cow
    if cow := Cow.query.get(id):
        return add_care(cow, cow_care, id, nb_cares_years(cow))
    lg.error(f"Cow with id {id} not found.")
    return  # ou lever une exception selon ta gestion d'erreur


def add_care(
    cow: Cow, cow_care: Tuple[date, dict, str], id: int, nb_cares_years: int
) -> tuple[int, date]:
    """Adds a care record to the specified cow and returns updated care information.

    This function appends a new care entry to the cow's care list, commits the change, and calculates the number of remaining cares and the date when a new care becomes available.

    Args:
        cow (Cow): The cow object to update.
        cow_cares (Tuple[date, dict, str]): The care information to add.
        id (int): The unique identifier for the cow.
        nb_cares_years (int): A function to calculate the number of cares in the current year.

    Returns:
        Tuple[int, date]: The number of remaining cares and the date of new available care.
    """
    # Ajouter le traitement à la liste
    cow.cow_cares.append(cow_care)

    # Commit les changements
    db.session.commit()
    lg.info(f"Care add to {id}.")

    nb_care = nb_cares_years(cow=cow)  # nombre de traitement dans l'année glissante
    remaining_care = 3 - nb_care  # traitement restant dans l'année glissante
    new_available_care = (
        cow.cow_cares[-nb_care][0] + timedelta(days=365)
        if len(cow.cow_cares) >= nb_care
        else cow.cow_cares[0][0] + timedelta(365)
    )  # date de disponibilité de nouveux traitement
    return remaining_care, new_available_care


def get_care_by_id(id: int) -> Optional[list[Tuple[date, dict, str]]]:
    """Retrieves the care records for a cow with the specified ID.

    Returns the list of care records for the cow if found, otherwise logs an error and returns None.

    Args:
        id (int): The unique identifier for the cow.

    Returns:
        Optional[Tuple[date, dict, str]]: The list of care records for the cow, or None if the cow is not found.
    """
    # Récupérer la vache depuis la BDD
    cow: Cow
    if cow := Cow.query.get(id):
        return cow.cow_cares
    lg.error(f"Cow with {id} not found.")
    return  # ou lever une exception selon ta gestion d'erreur


def get_care_on_year(year: int) -> list[Tuple[date, dict, str]]:
    """Retrieves all care records for all cows that occurred in a specific year.

    This function iterates through all cows and collects care records whose date matches the specified year.

    Args:
        year (int): The year to filter care records by.

    Returns:
        list[Tuple[date, dict, str]]: A list of care records from the specified year.
    """
    res = []
    cow: Cow
    for cow in Cow.query.all():
        res.extend(cow_care for cow_care in cow.cow_cares if cow_care[0].year == year)
    return res


def add_reproduction(id: int, insemination : date) -> None :
    # TODO docstring add_reproduction
    cow : Cow
    if cow := Cow.query.get(id) :
        cow.reproduction.append({
            "insemination": insemination,
            "ultrasound": None,
            "dry": None,  # À remplir plus tard
            "calving_preparation": None,
            "calving_date": None,
            "calving": False
        })
        lg.info(f'insemination on {date} add to {id}')
    else :
        lg.error(f'Cow with {id} not found.')
        

def reproduction_ultrasound(id: int, ultrasound : bool ) -> None:
    # TODO docstring reproduction_ultrasound
    cow : Cow
    if cow := Cow.query.get(id):
        reproduction : Reproduction  = cow.reproduction[-1][0]
        reproduction["ultrasound"] = ultrasound

        if ultrasound:
            set_reproduction(reproduction)
            lg.info(f'insemination on {date} of {id} confirm')
        else :
            lg.info(f'insemination on {date} of {id} invalidate')
    else : 
        lg.error(f'Cow with {id} not found.')


def set_reproduction(reproduction):
    # TODO docstring set_reproduction
    calving_date : date = reproduction["insemination"] + timedelta(days=280)
    user : Users = Users.query.get(1)
    calving_preparation_time = user.setting["calving_preparation_time"]
    dry_time = user.setting["dry_time"]

    reproduction["dry"] = calving_date - timedelta(days=dry_time)
    reproduction["calving_preparation"] = calving_date - timedelta(days=calving_preparation_time)
    reproduction["calving_date"] = calving_date
    

def remove_cow(id: int) -> None:
    """Marks a cow as no longer in the farm by updating its status.

    If the cow with the given ID exists, its status is updated and the change is committed. If the cow does not exist, a warning is logged.

    Args:
        id (int): The unique identifier for the cow to remove.

    Returns:
        None
    """
    cow: Cow
    if cow := Cow.query.get(id):
        cow.in_farm = False
        db.session.commit()
        lg.info(f"Cow {id} left the farm.")
    else:
        lg.warning(f"Cow with {id} not found.")


# END COW FONCTION


# PRESCRIPTION FONCTION


def add_prescription(date: date, care_items: dict[str, int]) -> None:
    """Adds a new prescription to the database with the specified date and care items.

    This function creates a new Prescription object, adds it to the database session, and commits the transaction.

    Args:
        date (date): The date of the prescription.
        care_items (dict[str, int]): The dictionary of care items to include in the prescription.

    Returns:
        None
    """
    prescription = Prescription(date=date, care=care_items, dlc_left=False)
    db.session.add(prescription)
    db.session.commit()


def get_all_prescription() -> List[Prescription]:
    """Retrieves all prescriptions from the database.

    This function queries the database and returns a list of all Prescription objects.

    Returns:
        List[Prescription]: A list of all prescriptions in the database.
    """
    return Prescription.query.all()


def get_year_prescription(year: int) -> List[Prescription]:
    """Retrieves all prescriptions from the database for a specific year.

    This function filters prescriptions by the given year and returns a list of matching Prescription objects.

    Args:
        year (int): The year to filter prescriptions by.

    Returns:
        List[Prescription]: A list of prescriptions from the specified year.
    """
    return Prescription.query.filter(
        (extract("year", Prescription.date) == year) & (Prescription.dlc_left == False)
    ).all()


def get_dlc_left_on_year(year: int) -> List[Prescription]:
    """Retrieves all prescriptions for which medication was removed to expired shelf life (DLC) in a specific year.

    This function filters prescriptions by the given year and returns those where the DLC (shelf life) has passed.

    Args:
        year (int): The year to filter prescriptions by.

    Returns:
        List[Prescription]: A list of prescriptions with medication removed due to expired DLC in the specified year.
    """
    return Prescription.query.filter(
        (extract("year", Prescription.date) == year) & (Prescription.dlc_left == True)
    ).all()


def add_medic_in_pharma_liste(medic: str) -> None:
    """Adds a new medication to the pharmacy list if it does not already exist.

    If the medication is not present in the pharmacy list, it is added and the change is committed. If it already exists, an error is logged.

    Args:
        medic (str): The name of the medication to add.

    Returns:
        None
    """
    pharma_liste: Prescription = Prescription.query.get(1)
    if medic not in pharma_liste.care:
        pharma_liste.care[medic] = 0  # ou None
        db.session.commit()
        lg.info(f"{medic} add in pharma list")
    else:
        lg.error(f"{medic} already in pharma list")


def get_pharma_liste() -> dict[str, int]:
    """Retrieves the pharmacy medication list as a dictionary.

    This function returns the care dictionary from the pharmacy Prescription entry in the database.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their quantities.
    """
    pharma_list: Prescription = Prescription.query.get(1)
    return pharma_list.care


# END PRESCRIPTION FONCTION

# PHARMACIE FONCTION


def get_pharmacie_year(year: int) -> Pharmacie:
    # TODO get_pharmacie_year
    raise NotImplementedError("get_pharmacie_year is not yet implemented")


def set_pharmacie_year(year: int, pharmacie: Pharmacie) -> None:
    # TODO set_pharmacie_year
    raise NotImplementedError("set_pharmacie_year is not yet implemented")


def upload_pharmacie_year(year: int, pharmacie: Pharmacie) -> None:
    # TODO set_pharmacie_year
    raise NotImplementedError("upload_pharmacie_year is not yet implemented")


# END PHARMACIE FONCTION

# USERS FONCTION

def add_user()->None:
    # TODO docstring add_user
    
    user = Users(setting={
        "dry_time" : 0,
        "calving_preparation_time" : 0
    })
    db.session.add(user)
    db.session.commit()

def set_user_setting(dry_time : int , calving_preparation: int) -> None :
    # TODO docstring set_user_setting

    user : Users
    user = Users.query.first()
    user.setting["dry_time"]=dry_time
    user.setting["calving_preparation_time"]=calving_preparation
        

# END USERS FONCTION