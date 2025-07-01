from typing import List, Optional, Tuple, TypedDict
from sqlalchemy import Column, Integer, PickleType, DATE, Boolean, JSON, extract
from sqlalchemy.ext.mutable import MutableList, MutableDict
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
import logging as lg

from .views import app

# Create database connection object
db = SQLAlchemy(app)

from .fonction import *

# TODO gestion exeption
# TODO gestion des log
# TODO correction de dict[a : b] en dict[a, b]
# TODO remplacer id par cow_id
# TODO Gestion du None dans la repro


class Reproduction(TypedDict):
    """Represents the reproduction record for a cow, including key dates and outcomes.

    This class stores insemination, ultrasound, dry period, calving preparation, calving date, and abortion status for a cow's reproductive cycle.
    """

    insemination: date
    ultrasound: Optional[bool]
    dry: date
    calving_preparation: date
    calving_date: date
    calving: bool
    abortion: bool


class Setting(TypedDict):
    """Represents user settings for dry time and calving preparation time.

    This class stores the number of days for the dry period and the calving preparation period for a user.
    """

    dry_time: int  # Temps de tarrisement (en jour)
    calving_preparation_time: int  # Temps de prepa vellage (en jour)


class Cow(db.Model):
    """Represents a cow in the database, including care records, annotations, status, birth date, and reproduction history.

    This class stores all relevant information about a cow, such as its unique ID, care events, farm status, birth date, and reproduction records.
    """

    id = Column(Integer, primary_key=True)  # numero Vache
    # liste de (date de traitement, traitement, info complementaire)
    cow_cares = Column(MutableList.as_mutable(PickleType), default=list, nullable=False)
    # liste de (date de l'annotation, annotation general)
    info = Column(MutableList.as_mutable(PickleType), default=list, nullable=False)
    in_farm = Column(Boolean)  # faux si vache sortie expoitation
    born_date = Column(DATE)
    reproduction = Column(
        MutableList.as_mutable(PickleType), default=list, nullable=False
    )

    def __init__(
        self,
        id: int,
        cow_cares: list[tuple[date, dict[str, int], str]],
        in_farm: bool,
        born_date: date,
        reproduction: list[tuple[Reproduction, str]],
    ):
        """Initializes a Cow object with the provided attributes.

        This constructor sets the cow's unique ID, care records, farm status, birth date, and reproduction history.

        Args:
            id (int): The unique identifier for the cow.
            cow_cares (list[tuple[date, dict[str, int], str]]): The list of care records for the cow.
            in_farm (bool): Indicates if the cow is currently in the farm.
            born_date (date): The birth date of the cow.
            reproduction (list[tuple[Reproduction, str]]): The list of reproduction records for the cow.
        """
        self.id = id
        self.cow_cares = cow_cares
        self.in_farm = in_farm
        self.born_date = born_date
        self.reproduction = reproduction


class Prescription(db.Model):
    """Represents a prescription record in the database, including date, care items, and DLC status.

    This class stores information about a prescription, such as its date, the medications prescribed, and whether it was removed due to expired shelf life (DLC).
    """

    id = Column(Integer, primary_key=True)  # id Prescription
    date = Column(DATE)  # date de la Prescription

    # Traitement stocké au format JSON en base
    care = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)

    dlc_left = Column(Boolean)

    def __init__(self, date: DATE, care: dict[str, int], dlc_left: bool):
        """Initializes a Prescription object with the provided date, care items, and DLC status.

        This constructor sets the prescription's date, care dictionary, and whether it was removed due to expired shelf life (DLC).

        Args:
            date (DATE): The date of the prescription.
            care (dict[str, int]): The medications and their quantities for the prescription.
            dlc_left (bool): True if the prescription is for medication removed due to expired DLC, False otherwise.
        """
        self.date = date
        self.care = care
        self.dlc_left = dlc_left


class Pharmacie(db.Model):
    """Represents a pharmacy record for a specific year, including medication statistics and remaining stock.

    This class stores annual pharmacy data such as medication entries, usage, removals, and remaining stock for inventory management.
    """

    year_id = Column(Integer, primary_key=True)

    total_enter = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_used = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_used_calf = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_out_dlc = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    total_out = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    remaining_stock = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)

    def __init__(
        self,
        year_id: int,
        total_enter: dict[str, int],
        total_used: dict[str, int],
        total_used_calf: dict[str, int],
        total_out_dlc: dict[str, int],
        total_out: dict[str, int],
        remaining_stock: dict[str, int],
    ):
        """Initializes a Pharmacie object with the provided annual medication statistics and stock.

        This constructor sets the year, medication entries, usage, removals, and remaining stock for the pharmacy record.

        Args:
            year_id (int): The year for the pharmacy record.
            total_enter (dict[str, int]): Total medication entered in the year.
            total_used (dict[str, int]): Total medication used in the year.
            total_used_calf (dict[str, int]): Total medication used for calves in the year.
            total_out_dlc (dict[str, int]): Total medication removed due to expired shelf life (DLC).
            total_out (dict[str, int]): Total medication taken out of the pharmacy.
            remaining_stock (dict[str, int]): Remaining stock of each medication at year end.
        """
        self.year_id = year_id
        self.total_enter = total_enter
        self.total_used = total_used
        self.total_used_calf = total_used_calf
        self.total_out_dlc = total_out_dlc
        self.total_out = total_out
        self.remaining_stock = remaining_stock


class Users(db.Model):
    """Represents a user in the database, including their settings for dry time and calving preparation time.

    This class stores user-specific configuration for managing cow care and reproduction cycles.
    """

    id = Column(Integer, primary_key=True)  # numero utilisateur
    setting = Column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )  # setting utilisateur

    def __init__(self, setting: Setting):
        """Initializes a Users object with the provided settings.

        This constructor sets the user's settings for dry time and calving preparation time.

        Args:
            setting (Setting): The user's settings containing dry time and calving preparation time.
        """
        self.setting = setting


def init_db() -> None:
    """Initializes the database by dropping all tables, recreating them, and adding default entries.

    This function resets the database, adds a default prescription and user, commits the changes, and logs a warning that the database has been initialized.

    Returns:
        None
    """
    db.drop_all()
    db.create_all()
    db.session.add(Prescription(date=None, care={}, dlc_left=True))
    UserUtils.add_user()
    db.session.commit()
    lg.warning("Database initialized!")


# COW FONCTION
class CowUntils:
    """Provides utility functions for managing cow records, care events, and reproduction data.

    This class contains static methods to add, update, retrieve, and manage cows and their associated care and reproduction records in the database.
    """

    @staticmethod
    def get_cow(cow_id: int) -> Cow:
        """Retrieves a cow by its ID from the database.

        This function queries the database for a cow with the specified ID and returns the Cow object if found.

        Args:
            cow_id (int): The unique identifier for the cow.

        Returns:
            Cow: The Cow object corresponding to the given ID.

        Raises:
            ValueError: If the cow with the given ID does not exist.
        """
        if cow := Cow.query.get(cow_id):
            return cow
        raise ValueError(f"Cow with ID {cow_id} not found")

    @staticmethod
    def get_all_cows() -> list[Cow]:
        """Retrieves all cows from the database.

        This function queries the database and returns a list of all Cow objects.

        Returns:
            list[Cow]: A list of all cows in the database.
        """
        return Cow.query.all()

    @staticmethod
    def upload_cow(id: int, born_date: date) -> None:
        """Adds a new cow to the database if it does not already exist.

        If a cow with the given ID is not present, it is created and added to the database. Otherwise, an error is logged.

        Args:
            id (int): The unique identifier for the cow to be uploaded.

        Returns:
            None
        """
        if not Cow.query.get(id):
            new_cow = Cow(
                id=id,
                cow_cares=[],
                in_farm=True,
                born_date=born_date,
                reproduction=[(None, None)],
            )
            db.session.add(new_cow)
            db.session.commit()
            lg.info(f"{id} : upload in database")
        else:
            lg.error(f"{id} : already in database")
            raise ValueError(f"{id} : already in database")

    @staticmethod
    def suppress_cow(cow_id: int) -> None:
        """Removes a cow from the database by its ID.

        This function deletes the cow with the specified ID from the database and commits the change. If the cow does not exist, an error is logged.

        Args:
            cow_id (int): The unique identifier for the cow to be removed.
            born_date (date): The birth date of the cow.

        Returns:
            None
        """
        if cow := Cow.query.get(cow_id):
            db.session.delete(cow)
            db.session.commit()
            lg.info(f"{cow_id} : delete in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    @staticmethod
    def add_calf(calf_id: int, born_date: date) -> None:
        """Adds a new calf to the database if it does not already exist.

        If a calf with the given ID is not present, it is created and added to the database. Otherwise, an error is logged and a ValueError is raised.

        Args:
            calf_id (int): The unique identifier for the calf to be added.
            born_date (date): The birth date of the calf.

        Returns:
            None
        """
        if not Cow.query.get(calf_id):
            new_cow = Cow(
                id=calf_id,
                cow_cares=[],
                in_farm=True,
                born_date=born_date,
                reproduction=[],
            )
            db.session.add(new_cow)
            db.session.commit()
            lg.info(f"{calf_id} : upload in database")
        else:
            lg.error(f"{calf_id} : already in database")
            raise ValueError(f"{calf_id} : already in database")

    @staticmethod
    def update_care(
        id: int, cow_care: Tuple[date, dict[str, int], str]
    ) -> Optional[tuple[int, date]]:
        """Updates the care record for a cow with the specified ID.

        If the cow exists, the care is added and a tuple with the number of remaining cares and the date of new available care. If the cow does not exist, an error is logged and None is returned.

        Args:
            id (int): The unique identifier for the cow.
            cow_cares (Tuple[date, dict, str]): The care information to add.

        Returns:
            Optional[tuple[int, date]]: The number of remaining cares and the date of new available care, or None if the cow is not found.
        """

        # Récupérer la vache depuis la BDD
        cow: Cow
        if cow := Cow.query.get(id):
            return CowUntils.add_care(cow, cow_care, id)
        lg.error(f"Cow with id {id} not found.")
        raise ValueError(f"{id} n'existe pas.")

    @staticmethod
    def add_care(
        cow: Cow, cow_care: Tuple[date, dict[str, int], str], id: int
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

        # traitement restant dans l'année glissante et date de nouveaux traitement diponible
        return remaining_care_on_year(cow=cow), new_available_care(cow=cow)

    @staticmethod
    def get_care_by_id(id: int) -> Optional[list[Tuple[date, dict[str, int], str]]]:
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
        raise ValueError(f"{id} n'existe pas.")

    @staticmethod
    def get_care_on_year(year: int) -> list[Tuple[date, dict[str, int], str]]:
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
            res.extend(
                cow_care for cow_care in cow.cow_cares if cow_care[0].year == year
            )
        return res

    @staticmethod
    def get_calf_care_on_year(year: int) -> list[Tuple[date, dict[str, int], str]]:
        """Retrieves all care records for calves that occurred in a specific year.

        This function collects care records for cows without reproduction records, or for cows whose care date is before or on their last insemination date, and returns those that match the specified year.

        Args:
            year (int): The year to filter calf care records by.

        Returns:
            list[Tuple[date, dict[str, int], str]]: A list of calf care records from the specified year.
        """
        res = []
        cow: Cow
        for cow in Cow.query.all():
            if len(cow.reproduction) == 0:
                res.extend(
                    cow_care for cow_care in cow.cow_cares if cow_care[0].year == year
                )
            else:
                res.extend(
                    cow_care
                    for cow_care in cow.cow_cares
                    if cow_care[0].year == year
                    and (
                        cow_care[0] <= cow.reproduction[-1][0].get("insemination")
                        if cow.reproduction[-1][0]
                        else False
                    )
                )
        return res

    @staticmethod
    def add_insemination(id: int, insemination: date) -> None:
        """Adds an insemination record to the specified cow.

        This function appends a new insemination event to the cow's reproduction history if the cow exists, otherwise logs an error and raises a ValueError.

        Args:
            id (int): The unique identifier for the cow.
            insemination (date): The date of the insemination event.

        Returns:
            None
        """  # TODO Gestion doublon add_reproduction
        cow: Cow
        if cow := Cow.query.get(id):
            cow.reproduction.append(
                (
                    {
                        "insemination": insemination,
                        "ultrasound": None,
                        "dry": None,  # À remplir plus tard
                        "calving_preparation": None,
                        "calving_date": None,
                        "calving": False,
                        "abortion": False,
                    },
                    "",
                )
            )
            db.session.commit()
            lg.info(f"insemination on {date} add to {id}")
        else:
            lg.error(f"Cow with {id} not found.")
            raise ValueError(f"{id} n'existe pas.")

    @staticmethod
    def validated_ultrasound(id: int, ultrasound: bool) -> None:
        """Validates or invalidates the ultrasound result for the latest insemination of a cow.

        This function updates the ultrasound status in the cow's reproduction record and, if confirmed, updates related reproduction dates. If the cow does not exist, an error is logged and a ValueError is raised.

        Args:
            id (int): The unique identifier for the cow.
            ultrasound (bool): The result of the ultrasound (True for confirmed, False for not confirmed).

        Returns:
            None
        """
        # TODO gestion pas d'insemination reproduction_ultrasound
        cow: Cow
        if cow := Cow.query.get(id):
            reproduction: Reproduction = cow.reproduction[-1][0]
            reproduction["ultrasound"] = ultrasound

            if ultrasound:

                cow.reproduction[-1] = CowUntils.set_reproduction(reproduction), ""
                lg.info(f"insemination on {date} of {id} confirm")
            else:
                lg.info(f"insemination on {date} of {id} invalidate")

            db.session.commit()
        else:
            lg.error(f"Cow with {id} not found.")
            raise ValueError(f"{id} n'existe pas.")

    @staticmethod
    def set_reproduction(reproduction: Reproduction) -> Reproduction:
        """Calculates and sets the key reproduction dates for a cow based on insemination and user settings.

        This function updates the reproduction dictionary with calculated dry, calving preparation, and calving dates.

        Args:
            reproduction (Reproduction): The reproduction record to update.

        Returns:
            Reproduction: The updated reproduction record with calculated dates.
        """
        calving_date: date = reproduction["insemination"] + timedelta(days=280)
        user: Users = Users.query.get(1)
        calving_preparation_time = int(user.setting["calving_preparation_time"])
        dry_time = int(user.setting["dry_time"])

        reproduction["dry"] = calving_date - timedelta(days=dry_time)
        reproduction["calving_preparation"] = calving_date - timedelta(
            days=calving_preparation_time
        )
        reproduction["calving_date"] = calving_date
        return reproduction

    @staticmethod
    def get_reproduction(id: int) -> Reproduction:
        """Retrieves the latest reproduction record for a cow by its ID.

        This function returns the most recent reproduction dictionary for the specified cow, or raises a ValueError if the cow does not exist.

        Args:
            id (int): The unique identifier for the cow.

        Returns:
            Reproduction: The latest reproduction record for the cow.

        Raises:
            ValueError: If the cow with the given ID does not exist.
        """
        cow: Cow
        if cow := Cow.query.get(id):
            return cow.reproduction[-1][0]
        else:
            raise ValueError(f"{id} n'existe pas.")

    @staticmethod
    def get_valide_reproduction() -> dict[int, Reproduction]:
        """Retrieves the latest valid reproduction records for all cows with a confirmed ultrasound.

        This function returns a dictionary mapping cow IDs to their most recent reproduction record where the ultrasound is confirmed.

        Returns:
            dict[int, Reproduction]: A dictionary of cow IDs to their valid reproduction records.
        """
        # TODO filtré naissance
        cows: list[Cow] = Cow.query.all()
        return {
            cow.id: cow.reproduction[-1][0]
            for cow in cows
            if cow.reproduction and cow.reproduction[-1][0].get("ultrasound")
        }

    @staticmethod
    def validated_calving(cow_id: int, abortion: bool) -> None:
        """Validates the calving event for a cow and records whether it was an abortion.

        This function updates the latest reproduction record for the specified cow to indicate a calving event and whether it was an abortion. If the cow does not exist, an error is logged and a ValueError is raised.

        Args:
            cow_id (int): The unique identifier for the cow.
            abortion (bool): True if the calving was an abortion, False otherwise.

        Returns:
            None
        """  # TODO gestion pas d'insemination reproduction_ultrasound calving
        cow: Cow
        if cow := Cow.query.get(cow_id):
            reproduction: Reproduction = cow.reproduction[-1][0]
            reproduction["calving"] = True
            reproduction["abortion"] = abortion

            lg.info(f"calving of of {cow_id} confirm")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
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
            raise ValueError(f"{id} n'existe pas.")

    @staticmethod
    def get_all_care() -> list[tuple[date, dict[str, int], int]]:
        """Retrieves all non-empty care records for all cows, sorted by date in descending order.

        This function collects all care records with non-empty treatment dictionaries from every cow and returns them as a list sorted by date, most recent first.

        Returns:
            list[tuple[date, dict[str, int], int]]: A list of tuples containing the care date, care dictionary, and cow ID.
        """
        all_cares: List[Tuple[date, dict[str, int], int]] = [
            (care_date, care_dict, cow.id)
            for cow in Cow.query.all()
            for care_date, care_dict, *_ in cow.cow_cares
            if care_dict  # ignore les soins vides
        ]
        all_cares.sort(key=lambda x: x[0], reverse=True)  # tri par date décroissante
        return all_cares


# END COW FONCTION


# PRESCRIPTION FONCTION
class PrescriptionUntils:
    """Provides utility functions for managing prescription records and pharmacy medication lists.

    This class contains static methods to add, update, and retrieve prescriptions and medication lists in the database.
    """

    @staticmethod
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

    @staticmethod
    def add_dlc_left(date: date, care_items: dict[str, int]) -> None:
        """Adds a new prescription to the database for medication removed due to expired shelf life (DLC).

        This function creates a new Prescription object with the DLC flag set to True, adds it to the database session, and commits the transaction.

        Args:
            date (date): The date of the medication removal.
            care_items (dict[str, int]): The dictionary of care items removed due to expired DLC.

        Returns:
            None
        """
        prescription = Prescription(date=date, care=care_items, dlc_left=True)
        db.session.add(prescription)
        db.session.commit()

    @staticmethod
    def get_all_prescription() -> List[Prescription]:
        """Retrieves all prescriptions from the database.

        This function queries the database and returns a list of all Prescription objects.

        Returns:
            List[Prescription]: A list of all prescriptions in the database.
        """
        return Prescription.query.all()

    @staticmethod
    def get_all_prescription_cares() -> List[tuple[date, dict[str, int], bool]]:
        """Retrieves all prescription care records, excluding the header, sorted by date in descending order.

        This function collects all prescription records, removes the first entry (assumed to be a header), and returns the remaining records as a list sorted by date, most recent first.

        Returns:
            List[tuple[date, dict[str, int], bool]]: A list of tuples containing the prescription date, care dictionary, and DLC flag.
        """
        all_cares: List[Tuple[date, dict[str, int], bool]] = [
            (prescription.date, prescription.care, prescription.dlc_left)
            for prescription in Prescription.query.all()
        ]
        all_cares.pop(0)  # suprimer l'entete
        all_cares.sort(key=lambda x: x[0], reverse=True)  # Tri décroissant sur la date
        return all_cares

    @staticmethod
    def get_year_prescription(year: int) -> List[Prescription]:
        """Retrieves all prescriptions from the database for a specific year.

        This function filters prescriptions by the given year and returns a list of matching Prescription objects.

        Args:
            year (int): The year to filter prescriptions by.

        Returns:
            List[Prescription]: A list of prescriptions from the specified year.
        """
        return Prescription.query.filter(
            (extract("year", Prescription.date) == year)
            & (Prescription.dlc_left == False)
        ).all()

    @staticmethod
    def get_dlc_left_on_year(year: int) -> List[Prescription]:
        """Retrieves all prescriptions for which medication was removed to expired shelf life (DLC) in a specific year.

        This function filters prescriptions by the given year and returns those where the DLC (shelf life) has passed.

        Args:
            year (int): The year to filter prescriptions by.

        Returns:
            List[Prescription]: A list of prescriptions with medication removed due to expired DLC in the specified year.
        """
        return Prescription.query.filter(
            (extract("year", Prescription.date) == year)
            & (Prescription.dlc_left == True)
        ).all()

    @staticmethod
    def add_medic_in_pharma_list(medic: str) -> None:
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

    @staticmethod
    def get_pharma_list() -> dict[str, int]:
        """Retrieves the pharmacy medication list as a dictionary.

        This function returns the care dictionary from the pharmacy Prescription entry in the database.

        Returns:
            dict[str, int]: A dictionary mapping medication names to their quantities.
        """
        pharma_list: Prescription = Prescription.query.get(1)
        return pharma_list.care


# END PRESCRIPTION FONCTION


# PHARMACIE FONCTION
class PharmacieUtils:
    """Provides utility functions for managing pharmacy records and annual medication statistics.

    This class contains static methods to retrieve, update, and create pharmacy records for specific years, as well as to manage medication stock and usage data.
    """

    @staticmethod
    def get_pharmacie_year(year: int) -> Pharmacie:
        """Retrieves the pharmacy record for a specific year.

        This function returns the Pharmacie object for the given year if it exists, otherwise raises a ValueError.

        Args:
            year (int): The year for which to retrieve the pharmacy record.

        Returns:
            Pharmacie: The pharmacy record for the specified year.

        Raises:
            ValueError: If the pharmacy record for the given year does not exist.
        """
        if pharmacie := Pharmacie.query.get(year):
            return pharmacie
        raise ValueError(f"{year} doesn't exist.")

    @staticmethod
    def updateOrDefault_pharmacie_year(year: int, default: Pharmacie) -> Pharmacie:
        """Updates the pharmacy record for a given year if it exists, or creates it with default values if not.

        This function updates all attributes of the existing pharmacy record for the specified year, or adds a new record with the provided default if none exists.

        Args:
            year (int): The year for which to update or create the pharmacy record.
            default (Pharmacie): The default Pharmacie object to use if no record exists.

        Returns:
            Pharmacie: The updated or newly created pharmacy record for the year.
        """
        pharmacie_db = Pharmacie.query.get(year)

        if pharmacie_db:
            for attr in default.__dict__:
                if not attr.startswith("_") and hasattr(pharmacie_db, attr):
                    setattr(pharmacie_db, attr, getattr(default, attr))
        else:
            db.session.add(default)
            pharmacie_db = default

        db.session.commit()
        return pharmacie_db

    @staticmethod
    def get_all_pharmacie() -> List[Pharmacie]:
        """Retrieves all pharmacy records from the database.

        This function queries the database and returns a list of all Pharmacie objects.

        Returns:
            List[Pharmacie]: A list of all pharmacy records in the database.
        """
        return Pharmacie.query.all()

    @staticmethod
    def set_pharmacie_year(
        year_id: int,
        total_used: dict[str, int],
        total_used_calf: dict[str, int],
        total_out_dlc: dict[str, int],
        total_out: dict[str, int],
        remaining_stock: dict[str, int],
    ) -> None:
        """Creates and saves a new pharmacy record for a specific year with the provided medication statistics.

        This function constructs a new Pharmacie object with the given data and commits it to the database.

        Args:
            year_id (int): The year for the pharmacy record.
            total_used (dict[str, int]): Total medication used in the year.
            total_used_calf (dict[str, int]): Total medication used for calves in the year.
            total_out_dlc (dict[str, int]): Total medication removed due to expired shelf life (DLC).
            total_out (dict[str, int]): Total medication taken out of the pharmacy.
            remaining_stock (dict[str, int]): Remaining stock of each medication at year end.

        Returns:
            None
        """
        pharmacie = Pharmacie(
            year_id=year_id,
            total_used=total_used,
            total_used_calf=total_used_calf,
            total_out_dlc=total_out_dlc,
            total_out=total_out,
            remaining_stock=remaining_stock,
        )
        db.session.add(pharmacie)
        db.session.commit()

    @staticmethod
    def upload_pharmacie_year(year: int, remaining_stock: dict[str, int]) -> None:
        """Creates and saves a new pharmacy record for a specific year with the provided remaining stock.

        This function adds a new Pharmacie object for the given year with empty statistics except for the provided remaining stock. If a record for the year already exists, it raises a ValueError.

        Args:
            year (int): The year for the pharmacy record.
            remaining_stock (dict[str, int]): Remaining stock of each medication at year end.

        Returns:
            None

        Raises:
            ValueError: If a pharmacy record for the given year already exists.
        """
        if Pharmacie.query.get(year):
            raise ValueError(f"{year} already existe.")

        pharmacie = Pharmacie(
            year_id=year,
            total_enter={},
            total_used={},
            total_used_calf={},
            total_out_dlc={},
            total_out={},
            remaining_stock=remaining_stock,
        )
        db.session.add(pharmacie)
        db.session.commit()


# END PHARMACIE FONCTION


# USERS FONCTION
class UserUtils:
    """Provides utility functions for managing user records and user-specific settings.

    This class contains static methods to add users, update user settings, and retrieve user configuration from the database.
    """

    @staticmethod
    def add_user() -> None:
        """Adds a new user to the database with default settings.

        This function creates a user with default dry time and calving preparation time settings and commits it to the database.

        Returns:
            None
        """

        user = Users(setting={"dry_time": 0, "calving_preparation_time": 0})
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def set_user_setting(dry_time: int, calving_preparation: int) -> None:
        """Updates the user's settings for dry time and calving preparation time.

        This function sets the dry time and calving preparation time values for the first user in the database and commits the changes.

        Args:
            dry_time (int): The number of days for the dry period.
            calving_preparation (int): The number of days for calving preparation.

        Returns:
            None
        """

        user: Users
        user = Users.query.first()
        user.setting["dry_time"] = dry_time
        user.setting["calving_preparation_time"] = calving_preparation
        db.session.commit()

    def get_user_setting() -> Setting:
        """Retrieves the current user's settings for dry time and calving preparation time.

        This function returns the settings dictionary for the first user in the database.

        Returns:
            Setting: The user's settings containing dry time and calving preparation time.
        """
        user: Users = Users.query.first()
        return user.setting


# END USERS FONCTION
