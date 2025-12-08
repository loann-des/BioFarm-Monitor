from typing import List, Optional, Tuple, TypedDict
from flask_login import UserMixin
from sqlalchemy import Column, Integer, PickleType, DATE, Boolean, JSON, String, extract, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.mutable import MutableList, MutableDict
from werkzeug.security import generate_password_hash
# from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta
import logging as lg

# from .views import app
from . import db

# Create database connection object
# db = SQLAlchemy(app)


# TODO gestion exeption
# TODO gestion des log
# TODO correction de dict[a : b] en dict[a, b]
# TODO remplacer id par cow_id
# TODO Gestion du None dans la repro


class Traitement(TypedDict):
    date_traitement: date
    medicaments: dict[str, int]  # [medicament,dosage]
    annotation: str


class Note(TypedDict):
    date_note: date
    information: str


class Reproduction(TypedDict):
    """Represents the reproduction record for a cow, including key dates and outcomes.

    This class stores insemination, ultrasound, dry period, calving preparation, calving date, and abortion status for a cow's reproductive cycle.
    """

    insemination: date
    ultrasound: Optional[bool]
    dry: date
    dry_status: bool  # status du tarrisement
    calving_preparation: date
    calving_preparation_status: bool  # status de prepa vellage
    calving_date: date
    calving: bool  # status du vellage
    abortion: bool
    reproduction_details: Optional[str]  # détails sur la reproduction


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

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cow_id = Column(Integer, nullable=False)  # numero Vache
    # liste de (date de traitement, traitement, info complementaire)
    cow_cares = Column(MutableList.as_mutable(
        JSON), default=list, nullable=False)  # TODO modifier access
    # liste de (date de l'annotation, annotation general)
    info = Column(MutableList.as_mutable(JSON),
                  default=list, nullable=False)
    in_farm = Column(Boolean)  # faux si vache sortie expoitation
    born_date = Column(DATE)  # date de naissance de la vache
    # liste de Reproduction
    reproduction = Column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    is_calf = Column(Boolean, default=False, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint(
            user_id,
            cow_id),
        {})

    def __init__(
        self,
        user_id: int,
        cow_id: int,
        cow_cares: list[Traitement] = None,
        info: list[Note] = None,
        in_farm: bool = True,
        born_date: date = None,
        reproduction: list[Reproduction] = None,
        is_calf: bool = False
    ):
        if cow_cares is None:
            cow_cares = []
        if info is None:
            info = []
        if reproduction is None:
            reproduction = []
        self.user_id = user_id
        self.cow_id = cow_id
        self.cow_cares = cow_cares
        self.info = info
        self.in_farm = in_farm
        self.born_date = born_date
        self.reproduction = reproduction
        self.is_calf = is_calf


class Prescription(db.Model):
    """Represents a prescription record in the database, including date, care items, and DLC status.

    This class stores information about a prescription, such as its date, the medications prescribed, and whether it was removed due to expired shelf life (DLC).
    """

    id = Column(Integer, primary_key=True)  # id Prescription
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DATE)  # date de la Prescription

    # Traitement stocké au format JSON en base
    care = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)

    dlc_left = Column(Boolean)
    # TODO pdf prescription scanné ?

    def __init__(self, user_id : int, date: DATE, care: dict[str, int], dlc_left: bool):
        """Initializes a Prescription object with the provided date, care items, and DLC status.

        This constructor sets the prescription's date, care dictionary, and whether it was removed due to expired shelf life (DLC).

        Args:
            date (DATE): The date of the prescription.
            care (dict[str, int]): The medications and their quantities for the prescription.
            dlc_left (bool): True if the prescription is for medication removed due to expired DLC, False otherwise.
        """
        self.user_id = user_id
        self.date = date
        self.care = care
        self.dlc_left = dlc_left


class Pharmacie(db.Model):
    """Represents a pharmacy record for a specific year, including medication statistics and remaining stock.

    This class stores annual pharmacy data such as medication entries, usage, removals, and remaining stock for inventory management.
    """
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year_id = Column(Integer)
    total_enter = Column(MutableDict.as_mutable(JSON),
                         default=dict, nullable=False)
    total_used = Column(MutableDict.as_mutable(JSON),
                        default=dict, nullable=False)
    total_used_calf = Column(MutableDict.as_mutable(
        JSON), default=dict, nullable=False)
    total_out_dlc = Column(MutableDict.as_mutable(JSON),
                           default=dict, nullable=False)
    total_out = Column(MutableDict.as_mutable(JSON),
                       default=dict, nullable=False)
    remaining_stock = Column(MutableDict.as_mutable(
        JSON), default=dict, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint(
            user_id,
            year_id),
        {})

    def __init__(
        self,
        user_id : int,
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
        self.user_id = user_id
        self.year_id = year_id
        self.total_enter = total_enter
        self.total_used = total_used
        self.total_used_calf = total_used_calf
        self.total_out_dlc = total_out_dlc
        self.total_out = total_out
        self.remaining_stock = remaining_stock


class Users(UserMixin, db.Model):
    """Represents a user in the database, including their settings for dry time and calving preparation time.

    This class stores user-specific configuration for managing cow care and reproduction cycles.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)  # numero utilisateur
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    setting = Column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )  # setting utilisateur
    medic_list = Column(MutableDict.as_mutable(JSON), default=dict, nullable=False)

    def __init__(self, email : str, password : str, setting: Setting):
        """Initializes a Users object with the provided settings.

        This constructor sets the user's settings for dry time and calving preparation time.

        Args:
            setting (Setting): The user's settings containing dry time and calving preparation time.
        """
        self.email = email
        self.password = password
        self.setting = setting
        self.medic_list = {}
        


def init_db() -> None:
    """Initializes the database by dropping all tables, recreating them, and adding default entries.

    This function resets the database, adds a default prescription and user, commits the changes, and logs a warning that the database has been initialized.

    Returns:
        None
    """
    db.drop_all()
    db.create_all()
    db.session.add(Prescription(user_id=1, date=None, care={}, dlc_left=True))
    UserUtils.add_user(email="adm@mail.com", password=generate_password_hash(password="adm"))
    db.session.commit()
    lg.warning("Database initialized!")


# COW FONCTION
class CowUntils:
    """Provides utility functions for managing cow records, care events, and reproduction data.

    This class contains static methods to add, update, retrieve, and manage cows and their associated care and reproduction records in the database.
    """

    # general cow functions ------------------------------------------------

    @staticmethod
    def get_cow(user_id : int, cow_id: int) -> Cow:
        """Retrieves a cow by its ID from the database.

        This function queries the database for a cow with the specified ID and returns the Cow object if found.

        Args:
            cow_id (int): The unique identifier for the cow.

        Returns:
            Cow: The Cow object corresponding to the given ID.

        Raises:
            ValueError: If the cow with the given ID does not exist.
        """
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return cow
        raise ValueError(f"Cow with ID {cow_id} not found")

    @staticmethod
    def get_all_cows(user_id : int = None) -> list[Cow]:
        """Retrieves all of a user cows from the database.

        This function queries the database and returns a list of all Cow objects.

        Returns:
            list[Cow]: A list for user of all his cows in the database.
            
        """
        return Cow.query.get({"user_id": user_id}) if user_id else Cow.query.all()
        

    @staticmethod
    def add_cow(user_id: int, cow_id, born_date: date = None) -> None:
        """Adds a new cow to the database if it does not already exist.

        If a cow with the given ID is not present, it is created and added to the database. Otherwise, an error is logged.

        Args:
            id (int): The unique identifier for the cow to be uploaded.

        Returns:
            None
        """
        if not Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            new_cow = Cow(
                user_id=user_id,
                cow_id=cow_id,
                born_date=born_date
            )
            db.session.add(new_cow)
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}) : upload in database")
        else:
            lg.error(f"(user :{user_id}, cow: {cow_id}) : already in database")
            raise ValueError(
                f"(user :{user_id}, cow: {cow_id}) : already in database")

    @staticmethod
    def update_cow(user_id: int, cow_id: int, **kwargs) -> None:
        """Updates the attributes of a cow in the database.

        This function retrieves the cow with the specified ID and updates its attributes based on the provided keyword arguments.

        Args:
            cow_id (int): The unique identifier for the cow to be updated.
            **kwargs: The attributes to update (e.g., in_farm, born_date, etc.).

        Returns:
            None
        """
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            for key, value in kwargs.items():
                setattr(cow, key, value)
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}) : updated in database")
        else:
            lg.error(f"(user :{user_id}, cow: {cow_id}) : not in database")
            raise ValueError(
                f"(user :{user_id}, cow: {cow_id}) : doesn't exist in database")

    @staticmethod
    def suppress_cow(user_id: int, cow_id: int) -> None:
        """Removes a cow from the database by its ID.

        This function deletes the cow with the specified ID from the database and commits the change. If the cow does not exist, an error is logged.

        Args:
            cow_id (int): The unique identifier for the cow to be removed.
            born_date (date): The birth date of the cow.

        Returns:
            None
        """
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            db.session.delete(cow)
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}) : delete in database")
        else:
            lg.error(f"(user :{user_id}, cow: {cow_id}) : not in database")
            raise ValueError(
                f"(user :{user_id}, cow: {cow_id}) : doesn't exist in database")

    @staticmethod
    def remove_cow(user_id: int, cow_id: int) -> None:
        """Marks a cow as no longer in the farm by updating its status.

        If the cow with the given ID exists, its status is updated and the change is committed. If the cow does not exist, a warning is logged.

        Args:
            id (int): The unique identifier for the cow to remove.

        Returns:
            None
        """
        cow: Cow
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm :
                raise ValueError(f"user :{user_id}, cow: {cow_id}: deja supprimé.")
            cow.in_farm = False
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}): left the farm.")
        else:
            lg.warning(f"(user :{user_id}, cow: {cow_id}): not found.")
            raise ValueError(
                f"(user :{user_id}, cow: {cow_id}): n'existe pas.")

    @staticmethod
    def add_calf(user_id: int, calf_id: int, born_date: date = None) -> None:
        """Adds a new calf to the database if it does not already exist.

        If a calf with the given ID is not present, it is created and added to the database. Otherwise, an error is logged and a ValueError is raised.

        Args:
            calf_id (int): The unique identifier for the calf to be added.
            born_date (date): The birth date of the calf.

        Returns:
            None
        """
        if not Cow.query.get({"user_id": user_id, "cow_id": calf_id}):
            new_cow = Cow(
                user_id=user_id,
                cow_id=calf_id,
                born_date=born_date,
                is_calf=True
            )
            db.session.add(new_cow)
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {calf_id}) : upload in database")
        else:
            lg.error(
                f"(user :{user_id}, cow: {calf_id}) : already in database")
            raise ValueError(
                f"(user :{user_id}, cow: {calf_id}) : already in database")

    # END general cow functions ------------------------------------------------

    # cow care functions ------------------------------------------------
    @staticmethod
    def add_cow_care(
        user_id: int, cow_id: int,  cow_care: Traitement
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
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return CowUntils.add_care(cow, cow_care)
        lg.error(f"(user :{user_id}, cow: {cow_id})  not found.")
        raise ValueError(f"(user :{user_id}, cow: {cow_id})  n'existe pas.")

    @staticmethod
    def add_care(
        cow: Cow, cow_care: Traitement
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

        from .fonction import remaining_care_on_year, new_available_care
        # Ajouter le traitement à la liste
        cow.cow_cares.append(cow_care)

        # Commit les changements
        db.session.commit()
        lg.info(f"Care add to (user :{cow.user_id}, cow: {cow.cow_id}).")

        # traitement restant dans l'année glissante et date de nouveaux traitement diponible
        return remaining_care_on_year(cow=cow), new_available_care(cow=cow)

    @staticmethod
    def update_cow_care(
        user_id: int, cow_id: int, care_index: int, new_care: Traitement
    ) -> None:
        cow: Cow
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            # Remplacement du soin dans la liste
            if care_index >= len(cow.cow_cares):
                raise IndexError("index out of bouns")

            cow.cow_cares[care_index] = new_care
            db.session.commit()

            lg.info(
                f"(user :{user_id}, cow: {cow_id}) : care updated in database")
        else:
            raise ValueError(
                f"(user :{user_id}, cow: {cow_id}) : doesn't exist in database")

    @staticmethod
    def delete_cow_care(user_id: int, cow_id: int, care_index: int) -> None:
        """Deletes a specific care record from a cow's care list.

        This function removes the care record at the specified index from the cow's care list and commits the change to the database.

        Args:
            cow_id (int): The unique identifier for the cow.
            care_index (int): The index of the care record to be deleted.

        Returns:
            None
        """
        cow: Cow
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            del cow.cow_cares[care_index]
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}) : care deleted in database")
        else:
            lg.error(f"(user :{user_id}, cow: {cow_id}) : not in database")
            raise ValueError(f"(user :{user_id}, cow: {cow_id}) : doesn't exist in database")

    @staticmethod
    def get_all_care(user_id : int) -> list[Tuple[Traitement, int]]:
        """Retrieves all non-empty care records for all cows, sorted by date in descending order.

        This function collects all care records with non-empty treatment dictionaries from every cow and returns them as a list sorted by date, most recent first.

        Returns:
            list[tuple[date, dict[str, int], int]]: A list of tuples containing the care date, care dictionary, and cow ID.
        """
        cows: List[Cow] = Cow.query.get({"user_id": user_id})
        all_cares: List[Traitement, int] = [
            (care_dict, cow.cow_id)
            for cow in cows    
            for care_dict in cow.cow_cares
            if bool(care_dict)
        ]
        # tri par date décroissante
        all_cares.sort(key=lambda x: x[0]["date_traitement"], reverse=True)
        return all_cares

    @staticmethod
    def get_care_by_id(user_id: int, cow_id: int,) -> list[Traitement]:
        """Retrieves the care records for a cow with the specified ID.

        Returns the list of care records for the cow if found, otherwise logs an error and returns None.

        Args:
            id (int): The unique identifier for the cow.

        Returns:
            Optional[Tuple[date, dict, str]]: The list of care records for the cow, or None if the cow is not found.
        """
        # Récupérer la vache depuis la BDD
        cow: Cow
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return cow.cow_cares
        lg.error(f"(user :{user_id}, cow: {cow_id}) : not found.")
        raise ValueError(f"(user :{user_id}, cow: {cow_id}) : n'existe pas.")

    @staticmethod
    def get_care_on_year(user_id : int , year: int) -> list[Traitement]:
        """Retrieves all care records for all cows that occurred in a specific year.

        This function iterates through all cows and collects care records whose date matches the specified year.

        Args:
            year (int): The year to filter care records by.

        Returns:
            list[Tuple[date, dict, str]]: A list of care records from the specified year.
        """
        cows : list[Cow]= Cow.query.get({"user_id": user_id})
        return [cow.cow_cares for cow in cows if cow.cow_cares["date_traitement"].year == year]
        #for cow in Cow.query.all():
        #    res.extend(
        #        cow_care for cow_care in cow.cow_cares if cow_care[0].year == year
        #    )
        #return res

    @staticmethod
    def get_calf_care_on_year(user_id : int, year: int) -> list[Tuple[Traitement]]:
        """Retrieves all care records for calves that occurred in a specific year.

        This function collects care records for cows without reproduction records, or for cows whose care date is before or on their last insemination date, and returns those that match the specified year.

        Args:
            year (int): The year to filter calf care records by.

        Returns:
            list[Tuple[date, dict[str, int], str]]: A list of calf care records from the specified year.
        """
        res = []
        cow: Cow
        for cow in Cow.query.get({"user_id": user_id}):
            has_no_repro = len(cow.reproduction) == 0
            last_repro = cow.reproduction[-1] if cow.reproduction else None
            last_insemination = last_repro.get(
                "insemination") if last_repro else None

            if has_no_repro :
                res.extend(
                    cow_care for cow_care in cow.cow_cares if cow_care[0].year == year
                )
            else :
                res.extend(
                    cow_care
                    for cow_care in cow.cow_cares
                    if cow_care[0].year == year
                    and last_insemination is not None
                    and cow_care[0] <= last_insemination
                )
        return res

    # END cow care functions ------------------------------------------------

    # reproduction functions ------------------------------------------------

    @staticmethod
    def add_insemination(user_id : int, cow_id: int, insemination: date) -> None:
        """Adds an insemination record to the specified cow.

        This function appends a new insemination event to the cow's reproduction history if the cow exists, otherwise logs an error and raises a ValueError.

        Args:
            id (int): The unique identifier for the cow.
            insemination (date): The date of the insemination event.

        Returns:
            None
        """  # TODO Gestion doublon add_reproduction
        cow: Cow
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            cow.reproduction.append(
                {
                    "insemination": insemination,
                    "ultrasound": None,
                    "dry": None,  # À remplir plus tard
                    "calving_preparation": None,
                    "calving_date": None,
                    "calving": False,
                    "abortion": False,
                },
            )
            db.session.commit()
            lg.info(f"insemination on {insemination} add to {cow_id}")
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def validated_ultrasound(user_id : int, cow_id: int, ultrasound: bool) -> None:
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
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            reproduction: Reproduction = cow.reproduction[-1]
            reproduction["ultrasound"] = ultrasound

            if ultrasound:

                cow.reproduction[-1] = CowUntils.set_reproduction(reproduction)
                lg.info(f"insemination on {date} of {cow_id} confirm")
            else:
                lg.info(f"insemination on {date} of {cow_id} invalidate")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def set_reproduction(reproduction: Reproduction) -> Reproduction: #TODO Pur calculatoir sortir ?
        """Calculates and sets the key reproduction dates for a cow based on insemination and user settings.

        This function updates the reproduction dictionary with calculated dry, calving preparation, and calving dates.

        Args:
            reproduction (Reproduction): The reproduction record to update.

        Returns:
            Reproduction: The updated reproduction record with calculated dates.
        """
        calving_date: date = reproduction["insemination"] + timedelta(days=280)
        user: Users = Users.query.get(1)
        calving_preparation_time = int(
            user.setting["calving_preparation_time"])
        dry_time = int(user.setting["dry_time"])

        reproduction["dry"] = calving_date - timedelta(days=dry_time)
        reproduction["calving_preparation"] = calving_date - timedelta(
            days=calving_preparation_time
        )
        reproduction["calving_date"] = calving_date
        return reproduction

    @staticmethod
    def get_reproduction(user_id : int, cow_id: int) -> Reproduction:
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
        if not (cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id})):
            raise ValueError(f"{cow_id} n'existe pas.")
        if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
        return cow.reproduction[-1]

    @staticmethod
    def reload_all_reproduction(user_id : int) -> None:
        from .fonction import last

        cows: list[Cow] = Cow.query.filter_by(user_id= user_id, in_farm=True).all()
        for cow in cows:
            if (last(cow.reproduction)
                and cow.reproduction[-1].get("ultrasound")
                    and not cow.reproduction[-1].get("calving")):

                cow.reproduction[-1] = CowUntils.set_reproduction(
                    cow.reproduction[-1])

        db.session.commit()
        lg.info("reproduction reload")

    @staticmethod
    def get_valide_reproduction(user_id : int) -> dict[int, Reproduction]:
        """Retrieves the latest valid reproduction records for all cows with a confirmed ultrasound.

        This function returns a dictionary mapping cow IDs to their most recent reproduction record where the ultrasound is confirmed.

        Returns:
            dict[int, Reproduction]: A dictionary of cow IDs to their valid reproduction records.
        """
        from .fonction import last
        cows: list[Cow] = Cow.query.filter_by(user_id=user_id, in_farm=True).all()
        return {
            cow.cow_id: cow.reproduction[-1]
            for cow in cows
            if last(cow.reproduction) and cow.reproduction[-1].get("ultrasound") and not cow.reproduction[-1].get("calving")
        }

    @staticmethod
    def validated_calving(cow_id: int, user_id : int, abortion: bool, info: str = None) -> None:
        """Validates the calving event for a cow and records whether it was an abortion.

        This function updates the latest reproduction record for the specified cow to indicate a calving event and whether it was an abortion. If the cow does not exist, an error is logged and a ValueError is raised.

        Args:
            cow_id (int): The unique identifier for the cow.
            abortion (bool): True if the calving was an abortion, False otherwise.

        Returns:
            None
        """  
            #TODO gestion pas d'insemination reproduction_ultrasound calving
            #TODO getstion info
        cow: Cow
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")

            reproduction: Reproduction = cow.reproduction[-1]
            reproduction["calving"] = True
            reproduction["abortion"] = abortion
            cow.reproduction[-1] = reproduction

            lg.info(f"calving of of {cow_id} confirm")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def validated_dry(user_id : int, cow_id: int) -> None:
        """Validates the dry for a cow.

        This function updates the latest reproduction record for the specified cow to indicate that the dry period has been completed. If the cow does not exist, an error is logged and a ValueError is raised.

        Args:
            cow_id (int): The unique identifier for the cow.

        Returns:
            None
        """
        cow: Cow
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")

            try:
                reproduction: Reproduction = cow.reproduction[-1]
                reproduction["dry_status"] = True
                cow.reproduction[-1] = reproduction

                lg.info(f"dry of of {cow_id} confirm")

                db.session.commit()
            except Exception as e:
                lg.error(f"Error updating dry status for cow {cow_id}: {e}")
                raise
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def validated_calving_preparation(user_id : int, cow_id: int) -> None:
        """Validates the calving preparation for a cow.

        This function updates the latest reproduction record for the specified cow to indicate that the calving preparation has been completed. If the cow does not exist, an error is logged and a ValueError is raised.

        Args:
            cow_id (int): The unique identifier for the cow.

        Returns:
            None
        """
        cow: Cow
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer") 
            reproduction: Reproduction = cow.reproduction[-1]
            reproduction["calving_preparation_status"] = True
            cow.reproduction[-1] = reproduction

            lg.info(f"calving preparation of of {cow_id} confirm")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def update_cow_reproduction(
        user_id: int,
        cow_id: int,
        repro_index: int,
        new_repro: Reproduction,
    ) -> None:
        """Updates a specific reproduction record for a cow.

        This function replaces the reproduction record at the specified index with a new reproduction dictionary and commits the change to the database.

        Args:
            cow_id (int): The unique identifier for the cow.
            repro_index (int): The index of the reproduction record to update.
            new_repro (Reproduction): The new reproduction record to set.

        Returns:
            None
        """
        cow: Cow
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            cow.reproduction[repro_index] = new_repro
            db.session.commit()
            lg.info(f"{cow_id} : reproduction updated in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    @staticmethod
    def delete_cow_reproduction(user_id: int, cow_id: int, repro_index: int) -> None:
        """Deletes a specific reproduction record from a cow's reproduction history.

        This function removes the reproduction record at the specified index and commits the change to the database. If the cow does not exist, an error is logged and a ValueError is raised.

        Args:
            cow_id (int): The unique identifier for the cow.
            repro_index (int): The index of the reproduction record to delete.

        Returns:
            None
        """
        cow: Cow
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            del cow.reproduction[repro_index]
            db.session.commit()
            lg.info(f"{cow_id} : reproduction deleted in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    # END reproduction functions ------------------------------------------------


# END COW FONCTION


# PRESCRIPTION FONCTION
class PrescriptionUntils:
    """Provides utility functions for managing prescription records and pharmacy medication lists.

    This class contains static methods to add, update, and retrieve prescriptions and medication lists in the database.
    """

    @staticmethod
    def add_prescription(user_id: int, date: date, care_items: dict[str, int]) -> None:
        """Adds a new prescription to the database with the specified date and care items.

        This function creates a new Prescription object, adds it to the database session, and commits the transaction.

        Args:
            date (date): The date of the prescription.
            care_items (dict[str, int]): The dictionary of care items to include in the prescription.

        Returns:
            None
        """
        prescription = Prescription(user_id=user_id, date=date, care=care_items, dlc_left=False)
        db.session.add(prescription)
        db.session.commit()

    @staticmethod
    def add_dlc_left(user_id: int, date: date, care_items: dict[str, int]) -> None:
        """Adds a new prescription to the database for medication removed due to expired shelf life (DLC).

        This function creates a new Prescription object with the DLC flag set to True, adds it to the database session, and commits the transaction.

        Args:
            date (date): The date of the medication removal.
            care_items (dict[str, int]): The dictionary of care items removed due to expired DLC.

        Returns:
            None
        """
        prescription = Prescription(user_id=user_id, date=date, care=care_items, dlc_left=True)
        db.session.add(prescription)
        db.session.commit()

    @staticmethod
    def get_all_prescription(user_id: int) -> List[Prescription]:
        """Retrieves all prescriptions from the database.

        This function queries the database and returns a list of all Prescription objects.

        Returns:
            List[Prescription]: A list of all prescriptions in the database.
        """
        return Prescription.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_all_prescription_cares(user_id: int) -> List[tuple[date, dict[str, int], bool]]:
        """Retrieves all prescription care records, excluding the header, sorted by date in descending order.

        This function collects all prescription records, removes the first entry (assumed to be a header), and returns the remaining records as a list sorted by date, most recent first.

        Returns:
            List[tuple[date, dict[str, int], bool]]: A list of tuples containing the prescription date, care dictionary, and DLC flag.
        """
        all_cares: List[Tuple[date, dict[str, int], bool]] = [
            (prescription.date, prescription.care, prescription.dlc_left)
            for prescription in (Prescription.query.filter_by(user_id=user_id).all())
        ]
        all_cares.pop(0)  # suprimer l'entete
        # Tri décroissant sur la date
        all_cares.sort(key=lambda x: x[0], reverse=True)
        return all_cares

    @staticmethod
    def get_year_prescription(user_id : int, year: int) -> List[Prescription]:
        """Retrieves all prescriptions from the database for a specific year.

        This function filters prescriptions by the given year and returns a list of matching Prescription objects.

        Args:
            year (int): The year to filter prescriptions by.

        Returns:
            List[Prescription]: A list of prescriptions from the specified year.
        """
        return Prescription.query.filter_by(user_id=user_id, dlc_left=False).filter(
            (extract("year", Prescription.date) == year)
        ).all()

    @staticmethod
    def get_dlc_left_on_year(user_id: int, year: int) -> List[Prescription]:
        """Retrieves all prescriptions for which medication was removed to expired shelf life (DLC) in a specific year.

        This function filters prescriptions by the given year and returns those where the DLC (shelf life) has passed.

        Args:
            year (int): The year to filter prescriptions by.

        Returns:
            List[Prescription]: A list of prescriptions with medication removed due to expired DLC in the specified year.
        """
        return Prescription.query.filter_by(user_id=user_id, dlc_left=True).filter(
            (extract("year", Prescription.date) == year)
        ).all()


# END PRESCRIPTION FONCTION


# PHARMACIE FONCTION
class PharmacieUtils:
    """Provides utility functions for managing pharmacy records and annual medication statistics.

    This class contains static methods to retrieve, update, and create pharmacy records for specific years, as well as to manage medication stock and usage data.
    """

    @staticmethod
    def get_pharmacie_year(user_id: int, year: int) -> Pharmacie:
        """Retrieves the pharmacy record for a specific year.

        This function returns the Pharmacie object for the given year if it exists, otherwise raises a ValueError.

        Args:
            year (int): The year for which to retrieve the pharmacy record.

        Returns:
            Pharmacie: The pharmacy record for the specified year.

        Raises:
            ValueError: If the pharmacy record for the given year does not exist.
        """
        if pharmacie := Pharmacie.query.get({"user_id" : user_id, "year_id" : year }):
            return pharmacie
        raise ValueError(f"{year} doesn't exist.")

    @staticmethod
    def updateOrDefault_pharmacie_year(user_id: int, year: int, default: Pharmacie) -> Pharmacie:
        """Updates the pharmacy record for a given year if it exists, or creates it with default values if not.

        This function updates all attributes of the existing pharmacy record for the specified year, or adds a new record with the provided default if none exists.

        Args:
            year (int): The year for which to update or create the pharmacy record.
            default (Pharmacie): The default Pharmacie object to use if no record exists.

        Returns:
            Pharmacie: The updated or newly created pharmacy record for the year.
        """
        pharmacie_db = Pharmacie.query.get({"user_id" : user_id, "year_id" : year })

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
    def get_all_pharmacie(user_id: int) -> List[Pharmacie]:
        """Retrieves all pharmacy records from the database.

        This function queries the database and returns a list of all Pharmacie objects.

        Returns:
            List[Pharmacie]: A list of all pharmacy records in the database.
        """
        return Pharmacie.query.filter_by(user_id=user_id).all()

    @staticmethod
    def set_pharmacie_year(
        user_id: int,
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
            user_id=user_id,
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
    def upload_pharmacie_year(user_id: int, year_id: int, remaining_stock: dict[str, int]) -> None:
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
        if Pharmacie.query.get({"user_id" : user_id, "year_id" : year_id}):
            raise ValueError(f"{year_id} already existe.")

        pharmacie = Pharmacie(
            user_id=user_id,
            year_id=year_id,
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
    def add_user(email : str, password : str) -> None:
        """Adds a new user to the database with default settings.

        This function creates a user with default dry time and calving preparation time settings and commits it to the database.

        Returns:
            None
        """

        user = Users(email=email, password=password, setting={"dry_time": 0, "calving_preparation_time": 0})
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def set_user_setting(user_id : int, dry_time: int, calving_preparation: int) -> None:
        """Updates the user's settings for dry time and calving preparation time.

        This function sets the dry time and calving preparation time values for the first user in the database and commits the changes.

        Args:
            dry_time (int): The number of days for the dry period.
            calving_preparation (int): The number of days for calving preparation.

        Returns:
            None
        """

        user: Users
        user = Users.query.get(user_id)
        user.setting["dry_time"] = dry_time
        user.setting["calving_preparation_time"] = calving_preparation
        db.session.commit()

    @staticmethod
    def get_user_setting(user_id : int) -> Setting:
        """Retrieves the current user's settings for dry time and calving preparation time.

        This function returns the settings dictionary for the first user in the database.

        Returns:
            Setting: The user's settings containing dry time and calving preparation time.
        """
        user: Users = Users.query.get(user_id)
        return user.setting

    @staticmethod
    def get_user(user_id):
        if user := Users.query.get(user_id):
            return user
        else:
            raise #TODO raise get_user mais peut etre pas apparament bug 
    @staticmethod
    def add_medic_in_pharma_list(user_id: int, medic: str, mesur: int) -> None:
        """Adds a new medication to the pharmacy list if it does not already exist.

        If the medication is not present in the pharmacy list, it is added and the change is committed. If it already exists, an error is logged.

        Args:
            medic (str): The name of the medication to add.

        Returns:
            None
        """
        user: Users = Users.query.get(user_id)
        user.medic_list.setdefault(medic,mesur)
        db.session.commit()
        lg.info(f"{medic} add in pharma list")


    @staticmethod
    def get_pharma_list(user_id: int) -> list[str] :
        """Retrieves the pharmacy medication list as a dictionary.

        This function returns the care dictionary from the pharmacy Prescription entry in the database.

        Returns:
            dict[str, int]: A dictionary mapping medication names to their quantities.
        """
        user : Users = Users.query.get(user_id)
        return user.medic_list

# END USERS FONCTION
