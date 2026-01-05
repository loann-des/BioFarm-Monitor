# Standard
import logging as lg
from typing import List, Optional, Tuple, TypedDict, Any

# Third-party
from datetime import date, datetime, timedelta
from flask_login import UserMixin

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    PickleType,
    PrimaryKeyConstraint,
    String,
    DATE,
    JSON,
    extract)

from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash


# Local
from . import db

# TODO gestion exeption
# TODO gestion des log
# TODO correction de dict[a : b] en dict[a, b]
# TODO remplacer id par cow_id
# TODO Gestion du None dans la repro


class Traitement(TypedDict):
    date_traitement: str  # date au format 'YYYY-MM-DD'
    medicaments: dict[str, int]  # [medicament,dosage]
    annotation: str


class Note(TypedDict):
    date_note: str  # date au format 'YYYY-MM-DD'
    information: str


class Reproduction(TypedDict):
    """Représente le statut reproductif d'une  vache.
    """

    insemination: str
    """Date d'insémination au format 'YYYY-MM-DD'."""

    ultrasound: bool | None
    """Résultats de l'échographie. True si la vache porte un veau, False
    sinon."""

    dry: str | None
    """Date de tarissement au format 'YYYY-MM-DD'."""

    dry_status: bool # status du tarrisement
    """Tarissement d'une vache. True si la vache est en tarissement, False
    sinon."""

    calving_preparation: str | None
    """Date de préparation au vêlage au format 'YYYY-MM-DD'."""

    calving_preparation_status: bool # status de prepa vellage
    """"""

    calving_date: str | None
    """Date de vêlage au format 'YYYY-MM-DD'."""

    calving: bool # status du vellage
    """"""
    abortion: bool
    """Avortement. True si un avortement a eu lieu, False sinon."""

    reproduction_details: str | None # détails sur la reproduction
    """Détails sur la reproduction"""


class Setting(TypedDict):
    """Stocke des réglages utilisateur, en l'occurrence les durées de
    tarissement et de préparation au vêlage.
    """

    dry_time: int  # Temps de tarrisement (en jour)
    calving_preparation_time: int  # Temps de prepa vellage (en jour)


class Cow(db.Model):
    """Représente une vache dans la base de données, incluant ses traitements,
    des notes générales, son statut, sa date de naissance et son historique de
    reproduction."""

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),
            nullable=False)
    cow_id: Mapped[int] = mapped_column(Integer, nullable=False)  # numero Vache

    cow_cares: Mapped[list[Traitement]] = mapped_column(
            MutableList.as_mutable(JSON),
            default=list,
            nullable=False) #TODO modif doc sur Type
    """Liste de traitements. Forme un tuple (date de traitement,
    traitement, notes)."""

    info: Mapped[list[Note]] = mapped_column(MutableList.as_mutable(JSON),
            default=list, nullable=False)#TODO modif doc sur Type
    """Notes générales. Forme une liste de tuples (date, contenu)."""

    in_farm: Mapped[bool] = mapped_column(Boolean)
    """True si la vache se trouve dans la ferme, False si elle en est sortie.""" #TODO modif doc sur Type

    # TODO: Determine exact type annotation for born_date
    born_date = mapped_column(Date)
    """Date de naissance de la vache."""

    reproduction: Mapped[list[Reproduction]] = mapped_column(MutableList.as_mutable(JSON),
            default=list, nullable=False) #TODO modif doc sur Type
    """Liste des reproductions de la vache."""

    is_calf: Mapped[bool] = mapped_column(Boolean, default=False,
            nullable=False)
    """True si la vache est une génisse, False sinon."""

    # TODO: Determine exact type annotation for __table_args__
    __table_args__ = (
        PrimaryKeyConstraint(
            user_id,
            cow_id),
        {})

    def __init__(
        self,
        user_id: int,
        cow_id: int,
        cow_cares: list[Traitement] | None = None,
        info: list[Note] | None = None,
        in_farm: bool = True,
        born_date: date | None = None,
        reproduction: list[Reproduction] | None = None,
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
    """Représente un traitement dans la base de données. Sont inclus la date de
    prescription, le contenu du traitement, et la date limite de consommation.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """Identifiant du traitement."""

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),
            nullable=False)

    # TODO: Determine exact type annotation for date
    date = mapped_column(Date, nullable=False)
    """Date de la prescription."""

    # Traitement stocké au format JSON en base
    care: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Informations sur le traitement, stocké au format JSON dans la base de
    données."""

    dlc_left: Mapped[bool] = mapped_column(Boolean)
    """True si remiser pour date limite de consommation est dépassée, False sinon."""

    # TODO pdf prescription scanné ?

    def __init__(self,
        user_id: int,
        date: DATE,
        care: dict[str, int],
        dlc_left: bool
    ):
        """Initialise un objet Prescription représentant un traitement avec les
        date de prescription, le contenu et la date de consommation fournis.

        Arguments:
            * date (DATE): La date de la prescription
            * care (dict[str, int]): Le contenu et les doses prévus par la
            prescription
            * dlc_left (bool): True si la date de consommation est atteinte,
            False sinon.
        """
        self.user_id = user_id
        self.date = date
        self.care = care
        self.dlc_left = dlc_left


class Pharmacie(db.Model):
    """Représente le bilan de la pharmacie pour une année. Inclut les
    statistiques des médicaments et l'état des stocks.

    Cette classe stocke les données annuelles de la pharmacie telles que les
    entrées, utilisations et retraits de traitements et les stocks restants pour
    le bilan.
    """

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),
            nullable=False)

    year: Mapped[int] = mapped_column(Integer)
    """Année du bilan de pharmacie."""

    total_enter: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Quantité de traitements entrés dans la pharmacie au cours de l'année.
    Forme un dictionnaire {<nom>: <quantité entrée>}."""

    total_used: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Quantité de traitements utilisés au cours de l'année. Forme un
    dictionnaire {<nom>: <quantité utilisée>}."""

    total_used_calf: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Quantité de traitement utilisés sur des veaux au cours de l'année. Forme
    un dictionnaire {<nom>: <quantité utilisée>}."""

    total_out_dlc: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Quantité de médicaments périmés éliminés au cours de l'année. Forme un
    dictionnaire {<nom>: <quantité éliminée>}."""

    total_out: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Quantité de médicaments retirés de la pharmacie au cours de l'année.
    Forme un dictionnaire {<nom>: <quantité retirée>}."""

    remaining_stock: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)
    """Stocks restants à la fin de l'année. Forme un dictionnaire
    {<nom>: <quantité>}."""

    # TODO: Determine exact type annotation for __table_args__
    __table_args__ = (
        PrimaryKeyConstraint(
            user_id,
            year),
        {})

    def __init__(
        self,
        user_id : int,
        year: int,
        total_enter: dict[str, int],
        total_used: dict[str, int],
        total_used_calf: dict[str, int],
        total_out_dlc: dict[str, int],
        total_out: dict[str, int],
        remaining_stock: dict[str, int],
    ):
        """Initialise un objet Pharmacie à partir des statistiques et stocks
        fournis.
        Ce constructeur initialise l'année, les entrées, usages et retraits de
        traitements et les stocks restants pour l'inventaire.

        Arguments:
            * year (int): Année du bilan de pharmacie
            * total_enter (dict[str, int]): Total des entrées de médicaments
            au cours de l'année
            * total_used (dict[str, int]): Quantité de médicaments utilisée au
            cours de l'année
            * total_used_calf (dict[str, int]): Quantité de médicaments utilisée
            sur des veaux au cours de l'année
            * total_out_dlc (dict[str, int]): Quantité de médicaments périmés
            éliminés au cours de l'année
            * total_out (dict[str, int]): Quantité de médicaments retirés du
            stock au cours de l'année
        """
        self.user_id = user_id
        self.year = year
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
    # db.session.add(Prescription(user_id=1, date=None, care={}, dlc_left=True))
    UserUtils.add_user(email="adm@mail.com", password=generate_password_hash(password="adm"))
    UserUtils.add_user(email="adm2@mail.com", password=generate_password_hash(password="adm"))
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
    def get_all_cows(user_id: Optional[int] = None) -> list[Cow]:
        """Retrieves all of a user cows from the database.

        This function queries the database and returns a list of all Cow objects.

        Returns:
            list[Cow]: A list for user of all his cows in the database.

        """
        return Cow.query.filter_by(user_id=user_id).all() if user_id else Cow.query.all()

    @staticmethod
    def add_cow(user_id: int, cow_id, born_date: Optional[date] = None) -> None:
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
        cow: Optional[Cow]
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
    def add_calf(user_id: int, calf_id: int, born_date: Optional[date] = None) -> None:
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
        cow: Optional[Cow]
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return CowUntils.add_care(cow, cow_care)
        lg.error(f"(user :{user_id}, cow: {cow_id})  not found.")
        raise ValueError(f"(user :{user_id}, cow: {cow_id})  n'existe pas.")

    @staticmethod
    def add_care(
        cow: Cow, cow_care: Traitement
    ) -> tuple[int, date]:
        #TODO Gestion des dates ptn
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
        cow: Optional[Cow]
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            # Remplacement du soin dans la liste
            if care_index >= len(cow.cow_cares):
                raise IndexError("index out of bounds")
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
        cow: Optional[Cow]
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
        cows: List[Cow] = Cow.query.filter_by(user_id=user_id).all()
        all_cares: List[Tuple[Traitement, int]] = [
            (care_dict, cow.cow_id)
            for cow in cows
            for care_dict in cow.cow_cares
            if bool(care_dict)
        ]
        # tri par date décroissante
        # TODO verif sort
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
        cow: Optional[Cow]
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return cow.cow_cares
        lg.error(f"(user :{user_id}, cow: {cow_id}) : not found.")
        raise ValueError(f"(user :{user_id}, cow: {cow_id}) : n'existe pas.")

    @staticmethod
    def get_care_on_year(user_id : int , year: int) -> list[Traitement]:
        from web_app.fonction import parse_date

        """Retrieves all care records for all cows that occurred in a specific year.

        This function iterates through all cows and collects care records whose date matches the specified year.

        Args:
            year (int): The year to filter care records by.

        Returns:
            list[Tuple[date, dict, str]]: A list of care records from the specified year.
        """

        return [cow_care 
                for cow in Cow.query.filter_by(user_id=user_id).all()
                for cow_care  in cow.cow_cares
                if parse_date(cow_care["date_traitement"]).year == year
                ]

    @staticmethod
    def get_calf_care_on_year(user_id : int, year: int) -> list[Traitement]:
        """Retrieves all care records for calves that occurred in a specific year.

        This function collects care records for cows without reproduction records, or for cows whose care date is before or on their last insemination date, and returns those that match the specified year.

        Args:
            year (int): The year to filter calf care records by.

        Returns:
            list[Tuple[date, dict[str, int], str]]: A list of calf care records from the specified year.
        """
        from web_app.fonction import parse_date
        res : list[Traitement] = []
        cow: Cow
        for cow in Cow.query.filter_by(user_id=user_id).all(): 
            # TODO verif integrité is_calf
            if cow.is_calf :
                res.append(cow_care 
                    for cow_care  in cow.cow_cares
                    if parse_date(cow_care["date_traitement"]).year == year # type: ignore
                )
            else :
                last_insemination = parse_date(cow.reproduction[-1]["insemination"]) if cow.reproduction else None
                res.append(
                    cow_care
                    for cow_care in cow.cow_cares
                    if parse_date(cow_care["date_traitement"]).year == year
                    and parse_date(cow_care["date_traitement"]) <= last_insemination # type: ignore
                ) if last_insemination else None
        return res

    # END cow care functions ------------------------------------------------

    # reproduction functions ------------------------------------------------

    @staticmethod
    def add_insemination(user_id : int, cow_id: int, insemination: str) -> None:
        """Adds an insemination record to the specified cow.

        This function appends a new insemination event to the cow's reproduction history if the cow exists, otherwise logs an error and raises a ValueError.

        Args:
            id (int): The unique identifier for the cow.
            insemination (date): The date of the insemination event.

        Returns:
            None
        """  # TODO Gestion doublon add_reproduction
        cow: Optional[Cow]
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            cow.reproduction.append(
                {
                    "insemination": insemination,
                    "ultrasound": None,
                    "dry":  None,
                    "dry_status":  False, # status du tarrisement
                    "calving_preparation":  None,
                    "calving_preparation_status": False, # status de prepa vellage
                    "calving_date":  None,
                    "calving":  False, # status du vellage
                    "abortion": False,
                    "reproduction_details": None # détails sur la reproduction
                }
            )
            cow.is_calf = False
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
        from web_app.fonction import last
        cow: Optional[Cow]
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            reproduction: Reproduction = last(cow.reproduction) # type: ignore
            if not reproduction : raise ValueError(f"cow : {cow_id} : n'as pas eté inseminé")
            reproduction["ultrasound"] = ultrasound

            if ultrasound:

                cow.reproduction[-1] = CowUntils.set_reproduction(user_id,reproduction)
                lg.info(f"insemination on {date} of {cow_id} confirm")
            else:
                lg.info(f"insemination on {date} of {cow_id} invalidate")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def set_reproduction(user_id: int, reproduction: Reproduction) -> Reproduction: #TODO Pur calculatoir sortir ?
        """Calculates and sets the key reproduction dates for a cow based on insemination and user settings.

        This function updates the reproduction dictionary with calculated dry, calving preparation, and calving dates.

        Args:
            reproduction (Reproduction): The reproduction record to update.

        Returns:
            Reproduction: The updated reproduction record with calculated dates.
        """
        from web_app.fonction import substract_date_to_str, sum_date_to_str
        user: Users = UserUtils.get_user(user_id=user_id)
        calving_date: str = sum_date_to_str(reproduction["insemination"],280)
        print("calving_date ok")
        reproduction["dry"] = substract_date_to_str(calving_date, int(user.setting["dry_time"])) # type: ignore
        print("dry ok")
        reproduction["calving_preparation"] = substract_date_to_str(calving_date, int(user.setting["calving_preparation_time"])) # type: ignore
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
        cow: Optional[Cow]
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
                    user_id,
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
    def validated_calving(cow_id: int, user_id : int, abortion: bool, info: Optional[str] = None) -> None:
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
        cow: Optional[Cow]
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
        cow: Optional[Cow]
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
        cow: Optional[Cow]
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
        cow: Optional[Cow]
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
        cow: Optional[Cow]
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
        prescription = Prescription(user_id=user_id, date=date, care=care_items, dlc_left=False)  # type: ignore
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
        prescription = Prescription(user_id=user_id, date=date, care=care_items, dlc_left=True) # type: ignore
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
            (extract("year", Prescription.date) == year) # type: ignore
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
            (extract("year", Prescription.date) == year) # type: ignore
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
        if pharmacie := Pharmacie.query.get({"user_id" : user_id, "year" : year }):
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
        pharmacie_db = Pharmacie.query.get({"user_id" : user_id, "year" : year })

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
        year: int,
        total_enter: dict[str, int],
        total_used: dict[str, int],
        total_used_calf: dict[str, int],
        total_out_dlc: dict[str, int],
        total_out: dict[str, int],
        remaining_stock: dict[str, int],
    ) -> None:
        """Creates and saves a new pharmacy record for a specific year with the provided medication statistics.

        This function constructs a new Pharmacie object with the given data and commits it to the database.

        Args:
            year (int): The year for the pharmacy record.
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
            year=year,
            total_enter=total_enter,
            total_used=total_used,
            total_used_calf=total_used_calf,
            total_out_dlc=total_out_dlc,
            total_out=total_out,
            remaining_stock=remaining_stock,
        )
        db.session.add(pharmacie)
        db.session.commit()

    @staticmethod
    def upload_pharmacie_year(user_id: int, year: int, remaining_stock: dict[str, int]) -> None:
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
        if Pharmacie.query.get({"user_id" : user_id, "year" : year}):
            raise ValueError(f"{year} already existe.")

        pharmacie = Pharmacie(
            user_id=user_id,
            year=year,
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

        user: Users = Users.query.get(user_id) # type: ignore
        user.setting["dry_time"] = dry_time # type: ignore
        user.setting["calving_preparation_time"] = calving_preparation # type: ignore
        db.session.commit()

    @staticmethod
    def get_user_setting(user_id : int) -> Setting:
        """Retrieves the current user's settings for dry time and calving preparation time.

        This function returns the settings dictionary for the first user in the database.

        Returns:
            Setting: The user's settings containing dry time and calving preparation time.
        """
        user: Users = Users.query.get(user_id) # type: ignore
        return user.setting # type: ignore

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
        user: Users = Users.query.get(user_id) # type: ignore
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
        user : Users = Users.query.get(user_id) # type: ignore
        return user.medic_list # type: ignore

# END USERS FONCTION
