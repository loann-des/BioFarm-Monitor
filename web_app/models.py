# Standard
import logging as lg

from datetime import date
from flask_login import UserMixin
from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    DATE,
    JSON,
    extract)
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.orm import Mapped, mapped_column
from typing import TypedDict, Any
from werkzeug.security import generate_password_hash

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
    born_date : Mapped[date | None] = mapped_column(Date, nullable=True)
    """Date de naissance de la vache."""

    reproduction: Mapped[list[Reproduction]] = mapped_column(MutableList.as_mutable(JSON),
            default=list, nullable=False) #TODO modif doc sur Type
    """Liste des reproductions de la vache."""

    is_calf: Mapped[bool] = mapped_column(Boolean, default=False,
            nullable=False)
    """True si la vache est une génisse, False sinon."""

    #TODO refaire fonction avec cette arg
    init_as_cow : Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """True si la vache est comme vache adult, False sinon."""


    __table_args__: tuple[PrimaryKeyConstraint, dict[str, Any]] = (
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
        is_calf: bool = False,
        init_as_cow: bool = False
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
        self.init_as_cow = init_as_cow


class Prescription(db.Model):
    """Représente un traitement dans la base de données. Sont inclus la date de
    prescription, le contenu du traitement, et la date limite de consommation.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """Identifiant du traitement."""

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),
            nullable=False)

    date: Mapped[Date] = mapped_column(Date, nullable=False)
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

    __table_args__: tuple[PrimaryKeyConstraint, dict[str, Any]] = (
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
    """Représente un utilisateur dans la base de données. Inclut les durées de
    tarissement et de préparation du vêlage.

    Cette classe contient la configuration utilisateur de gestion des
    traitements et cycles reproductifs.
    """
    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # numero utilisateur
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    setting: Mapped[Setting] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )  # setting utilisateur
    medic_list: Mapped[dict[Any, Any]] = mapped_column(MutableDict.as_mutable(JSON),
            default=dict, nullable=False)

    def __init__(self, email : str, password : str, setting: Setting):
        """Initialise un objet Users avec les arguments fournis.
        Ce constructeur définit les paramètres utilisateurs pour les durées de
        tarissement et de préparation au vêlage.

        Arguments:
            * email (str): L'adresse e-mail de l'utilisateur
            * password (str): Le mot de passe de l'utilisateur
            * setting (Setting): un objet Setting représentant les réglages de
            l'utilisateur
        """
        self.email = email
        self.password = password
        self.setting = setting
        self.medic_list = {}



def init_db() -> None:
    """Initialise la base de données. Pour ce faire, supprime toutes les tables,
    les re-créée et les remplit avec les entrées par défaut.

    Cette fonction réinitialise la base de données, ajoute des utilisateurs,
    enregistre les changements (commit) et marque dans le journal que la base
    de données a été réinitialisée.
    """
    db.drop_all()
    db.create_all()
    # db.session.add(Prescription(user_id=1, date=None, care={}, dlc_left=True))
    UserUtils.add_user(email="adm@mail.com",
            password=generate_password_hash(password="adm"))
    UserUtils.add_user(email="adm2@mail.com",
            password=generate_password_hash(password="adm"))
    db.session.commit()
    lg.warning("Database initialized!")


# COW FONCTION
class CowUtils:
    """Cette classe est un namespace. Tous ses membres sont statiques.

    Ce namespace regroupe les fonctions de gestion des vaches, de
    l'historique des traitements, et des données de reproduction.
    """

    # general cow functions ------------------------------------------------

    @staticmethod
    def get_cow(user_id : int, cow_id: int) -> Cow:
        """Recherche une vache dans la base de données et renvoie un objet Cow
        si la vache a été trouvée.

        Arguments:
            * cow_id (int): Identifiant de la vache recherchée.

        Renvoie:
            * Cow: L'objet Cow correspondant à la vache associée à cow_id.

        Lance:
            * ValueError si la vache recherchée n'existe pas dans la base de
            données.
        """

        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return cow
        raise ValueError(f"Cow with ID {cow_id} not found")

    @staticmethod
    def get_all_cows(user_id: int | None = None) -> list[Cow]:
        """Renvoie l'ensemble des vaches d'un utilisateur.

        Cette fonction interroge la base de données et renvoie une liste de
        toutes les vaches associées à un utilisateur.

        Renvoie:
            * list[Cow]: Une liste contenant l'ensemble des vaches d'un
            utilisateur
        """
        return Cow.query.filter_by(user_id=user_id).all() if user_id else Cow.query.all()

    @staticmethod
    def add_cow(user_id: int, cow_id: int, born_date: date | None = None,
            init_as_cow: bool = False) -> None:
        """Ajoute une nouvelle vache à la base de données si elle n'existe pas
        déjà.

        Si aucune vache avec l'identifiant correspondant n'existe, alors elle
        est ajoutée à la base de données. Sinon une erreur est marquée dans le
        journal.

        Arguments:
            * id (int): Identifiant de la vache à ajouter
        """
        if not Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            new_cow = Cow(
                user_id=user_id,
                cow_id=cow_id,
                born_date=born_date,
                init_as_cow=init_as_cow
            )
            db.session.add(new_cow)
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}) : upload in database")
        else:
            lg.error(f"(user :{user_id}, cow: {cow_id}) : already in database")
            raise ValueError(
                f"(user :{user_id}, cow: {cow_id}) : already in database")

    @staticmethod
    def update_cow(user_id: int, cow_id: int, **kwargs: dict[str, Any]) -> None:
        """Met à jour les attributs d'une vache dans la base de données.

        Cette fonction recherche la vache associée à l'identifiant fourni, et
        met à jour ses attributs à partir des arguments nommés (kwargs).

        Arguments:
            * cow_id (int): Identifiant de la vache à modifier
            * **kwargs (dict[str, Any]): Les attributs à modifier (e.g. in_farm,
            born_date, etc.)
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
        """Retire une vache associée à un identifiant de la base de données.

        Cette fonction retire de la base de données la vache associée à
        l'identifiant fourni en argument et enregistre (commit) les changements.
        Si la vache n'existe pas, une erreur est marquée dans le journal.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
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
        """Enregistre la sortie d'une vache de la ferme en mettant à jour le
        statut de la vache.

        Si la vache associée à l'identifiant fourni existe, son statut est mis
        à jour et enregistré (commit) dans la base de données. Si la vache
        n'existe pas, une erreur est marquée dans le journal.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache à retirer de la ferme
        """
        cow: Cow | None
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
    def add_calf(user_id: int, calf_id: int,
            born_date: date | None = None) -> None:
        """Ajoute un veau à la base de données s'il n'existe pas déjà.

        S'il n'existe pas de veau associé à l'identifiant fourni, il est créé
        et ajouté à la base de données. Autrement, une erreur est marquée dans
        le journal et une ValueError est lancée.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * calf_id (int): Identifiant du veau
            * born_date (date): Date de naissance du veau

        Lance:
            * ValueError s'il existe déjà un veau associé à l'identifiant fourni
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
    ) -> tuple[int, date | None]:
        """Met à jour l'historique des traitements de la vache associée à
        l'identifiant fourni en argument.

        Si la vache existe, le traitement est ajouté et un tuple contenant le
        nombre de traitement restants et la date des prochains traitements est
        créé. Si la vache n'existe pas, une erreur est marquée dans le journal
        et la fonction renvoie None.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * cow_care (Traitement): Traitement à ajouter

        Retourne:
            * tuple ([int, date] | None): le nombre de traitements restants et
            la date du prochain, ou None si aucune vache associée à cow_id n'a
            été trouvée
        """

        # Récupérer la vache depuis la BDD
        cow: Cow | None
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return CowUtils.add_care(cow, cow_care)
        lg.error(f"(user :{user_id}, cow: {cow_id})  not found.")
        raise ValueError(f"(user :{user_id}, cow: {cow_id})  n'existe pas.")

    @staticmethod
    def add_care(
        cow: Cow, cow_care: Traitement
    ) -> tuple[int, date | None]:
        #TODO Gestion des dates ptn
        """Ajoute un traitement à la vache spécifiée et renvoie les données de
        traitement mises à jour.

        Cette fonction ajoute une nouvelle entrée à la liste des traitements
        de la vache associée à l'identifiant fourni, enregistre (commit) les
        modifications, et calcule le nombre de traitements restants et la date
        du suivant.

        Arguments:
            * cow (Cow): L'objet Cow à mettre à jour
            * cow_cares (Tuplee[date, dict, str]): Les informations de
            traitement à ajouter

        Renvoie:
        * tuple[int, date]: Le nombre de traitements restants et la date du
        prochain
        """

        from .fonction import remaining_care_on_year, new_available_care
        # Ajouter le traitement à la liste
        cow.cow_cares.append(cow_care)

        # Commit les changements
        db.session.commit()

        lg.info(f"Care add to (user :{cow.user_id}, cow: {cow.cow_id}).")

        # traitement restant dans l'année glissante et date de nouveaux traitement diponible
        return remaining_care_on_year(cow=cow), new_available_care(cow=cow) # type: ignore

    @staticmethod
    def update_cow_care(
        user_id: int, cow_id: int, care_index: int, new_care: Traitement
    ) -> None:
        """Met à jour la liste de traitements d'une vache.

        Cette fonction met à jour la liste de traitements d'une vache au sein de
        la base de données. Lance une ValueError si aucune vache ne correspond
        à l'identifiant spécifié, et lance une IndexError si le traitement
        n'existe pas déjà dans la base de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache concernée
            * care_index (int): Position dans la liste du traitement à modifier
            * new_care (Traitement): Nouvelles données de traitement
        """
        cow: Cow | None
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
        """Retire un traitement de la liste de traitements d'une vache

        Cette fonction retire le traitement à l'indice spécifié de la liste de
        traitements de la vache associée à l'identifiant fourni et enregistre
        (commit) le changement dans la base de données

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * care_index (int): Indice du traitement dans la liste
        """
        cow: Cow | None
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            del cow.cow_cares[care_index]
            db.session.commit()
            lg.info(f"(user :{user_id}, cow: {cow_id}) : care deleted in database")
        else:
            lg.error(f"(user :{user_id}, cow: {cow_id}) : not in database")
            raise ValueError(f"(user :{user_id}, cow: {cow_id}) : doesn't exist in database")

    @staticmethod
    def get_all_care(user_id : int) -> list[tuple[Traitement, int]]:
        """Retrieves all non-empty care records for all cows, sorted by date in descending order.

        This function collects all care records with non-empty treatment dictionaries from every cow and returns them as a list sorted by date, most recent first.

        Returns:
            list[tuple[date, dict[str, int], int]]: A list of tuples containing the care date, care dictionary, and cow ID.
        """
        cows: list[Cow] = Cow.query.filter_by(user_id=user_id).all()
        all_cares: list[tuple[Traitement, int]] = [
            (care_dict, cow.cow_id)
            for cow in cows
            for care_dict in cow.cow_cares
            if bool(cow.cow_cares) and bool(care_dict)
        ]
        # tri par date décroissante
        # TODO verif sort
        all_cares.sort(key=lambda x: x[0]["date_traitement"], reverse=True)
        return all_cares

    @staticmethod
    def get_care_by_id(user_id: int, cow_id: int,) -> list[Traitement] | None:
        """Renvoie la liste des traitements d'une vache

        Renvoie la liste des traitements de la vache associée à l'identifiant
        fourni si elle existe. Sinon, marque une erreur dans le journal et
        renvoie None.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Renvoie:
            * list[Traitement] | : La liste des traitements de la vache
            spécifiéé si elle existe, None sinon
        """
        # Récupérer la vache depuis la BDD
        cow: Cow | None
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            return cow.cow_cares
        lg.error(f"(user :{user_id}, cow: {cow_id}) : not found.")
        raise ValueError(f"(user :{user_id}, cow: {cow_id}) : n'existe pas.")

    @staticmethod
    def get_care_on_year(user_id : int , year: int) -> list[Traitement]:
        """Récupère la liste des traitements sur l'ensemble des vaches effectués
        l'année spécifiée.

        Cette fonction itère sur l'ensemble des vaches et collecte les
        traitements dont l'année correspond à l'année fournie en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année à laquelle ont eu lieu les traitements que l'on
            souhaite collecter

        Renvoie:
            * list[Traitement]: La liste des traitements qui ont eu lieu l'année
            spécifiée
        """
        from web_app.fonction import parse_date

        return [cow_care
                for cow in Cow.query.filter_by(user_id=user_id).all()
                for cow_care  in cow.cow_cares if bool(cow.cow_cares)
                if parse_date(cow_care["date_traitement"]).year == year
                ]

    @staticmethod
    def get_calf_care_on_year(user_id : int, year: int) -> list[Traitement]:
        """Récupère l'ensemble de l'historique de traitement des veaux sur une
        année spécifique.

        Cette fonction collecte l'ensemble des traitements effectués sur les
        vaches sans historique de reproduction et les traitements effectués  sur
        les vaches avant la date de leur première insémination, et les filtre
        pour correspondre à l'année fournie en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur.
            * year (int): Année au cours de laquelle ont eu lieu les
           traitements.

        Renvoie:
            * list[Traitement]: Une liste de traitements sur les veaux datant
            de l'année fournie en argument
        """
        from web_app.fonction import parse_date
        # res : list[Traitement] = []
        # cow: Cow
        # for cow in Cow.query.filter_by(user_id=user_id).all():
            # TODO verif integrité is_calf
            # res.extend(
            #         cow_care
            #         for cow_care in cow.cow_cares
            #         if (
            #             parse_date(cow_care["date_traitement"]).year == year #verif de l'anné
            #             and (
            #                 cow.is_calf # si c'est un veaux
            #                 or (        # sinon
            #                     cow.reproduction   #si il y'a eu reproduction
            #                     and parse_date(cow_care["date_traitement"]) <= parse_date(cow.reproduction[-1]["insemination"]) # traitement avant reproduction
            #                     )
            #                 )
            #             )
            # )
        res : list[Traitement] = [
            cow_care
            for cow in Cow.query.filter_by(user_id=user_id).all()   #iteration sur cows
            for cow_care in cow.cow_cares                           #iteration sur cow_care
            if (
                parse_date(cow_care["date_traitement"]).year == year #verif de l'année
                and (
                    cow.is_calf            # si c'est un veau
                    or (
                        not cow.init_as_cow # sinon : non initialiser comme vache
                        and cow.reproduction   # et si il y'a eu reproduction
                        and parse_date(cow_care["date_traitement"]) <= parse_date(cow.reproduction[0]["insemination"]) # et si traitement avant reproduction
                        )
                    )
                )
        ]


            # if cow.is_calf:
            #     res.extend(
            #         cow_care
            #         for cow_care in cow.cow_cares
            #         if parse_date(cow_care["date_traitement"]).year == year
            #     )
            # else:
            #     last_insemination = parse_date(cow.reproduction[-1]["insemination"]) if cow.reproduction else None
            #     if last_insemination:
            #         res.extend(
            #             cow_care
            #             for cow_care in cow.cow_cares
            #             if (
            #                 parse_date(cow_care["date_traitement"]).year == year
            #                 and parse_date(cow_care["date_traitement"])<= last_insemination
            #             )
            #         )
        return res

    # END cow care functions ------------------------------------------------

    # reproduction functions ------------------------------------------------

    @staticmethod
    def add_insemination(user_id : int, cow_id: int, insemination: str) -> None:
        # TODO Gestion doublon add_reproduction
        """Ajoute une entrée à l'historique d'insémination de la vache spécifiée

        Cette fonction ajoute une nouvelle insémination à l'historique de
        reproduction de la vache associée à l'identifiant fourni comme argument
        si elle existe. Sinon, marque une erreur dans le journal et lance une
        ValueError.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * insemination (str): Date d'insémination

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
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
        """Valide ou invalide les résultats des ultrasons pour la dernière
        insémination d'une vache.

        Cette fonction met à jour les résultats des ultrasons dans l'historique
        de reproduction de la vache associée à l'identifiant fourni, ainsi que
        les dates de reproduction associées.Si la vache spécifiée n'existe pas,
        une ValueError est lancée.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * ultradound (bool): Résultats des ultrasons (True si confirmé,
            False si non confirmé)

        Lance:
            * ValueError si aucune vache dans la base n'est associée à
            l'identifiant fourni
        """
        from web_app.fonction import last
        cow: Cow | None
        if cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id}):
            if not cow.in_farm : raise ValueError(f"cow : {cow_id} : est supprimer")
            reproduction: Reproduction | None = last(cow.reproduction) # type: ignore
            if not reproduction:
                raise ValueError(f"cow : {cow_id} : n'as pas eté inseminé")
            reproduction["ultrasound"] = ultrasound

            if ultrasound:

                cow.reproduction[-1] = CowUtils.set_reproduction(user_id,reproduction)
                lg.info(f"insemination on {date} of {cow_id} confirm")
            else:
                lg.info(f"insemination on {date} of {cow_id} invalidate")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    @staticmethod
    def set_reproduction(user_id: int, reproduction: Reproduction) -> Reproduction: #TODO Pur calculatoir sortir ?
        """Calcule les dates de reproduction pour une vache en fonction de sa
        date d'insémination et des réglages utilisateur.

        Cette fonction met à jour le dictionnaire de reproduction avec les
        durées de tarissage, de préparation et la date de vêlage calculés.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * reproduction (Reproduction): Les données de reproduction à mettre
            à jour

        Renvoie:
            * Reproduction: Les données de reproduction mises à jour, avec les
            dates calculées
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
        """Récupère la dernière reproduction de la vache spécifiée.

        Cette fonction renvoie l'entrée de reproduction la plus récente de la
        vache spécifiée, ou lance une ValueError si aucune vache n'est associée
        à l'identifiant fourni en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Renvoie:
            * Reproduction: l'entrée de reproduction la plus récente pour la
            vache concernée

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if not (cow := Cow.query.get({"user_id": user_id, "cow_id": cow_id})):
            raise ValueError(f"{cow_id} n'existe pas.")
        if not cow.in_farm:
            raise ValueError(f"cow : {cow_id} : est supprimer")
        return cow.reproduction[-1]

    @staticmethod
    def reload_all_reproduction(user_id : int) -> None:
        """Recalcule les dates associées à la dernière reproduction des vaches.

        Cette fonction parcourt la liste des vaches et recalcule pour chacune
        les dates clefs liées à la reproduction la plus récente dans son
        historique et enregistre (commit) les changements dans la base de
        données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
        """
        from .fonction import last

        cows: list[Cow] = Cow.query.filter_by(user_id= user_id, in_farm=True).all()
        for cow in cows:
            if (last(cow.reproduction)
                and cow.reproduction[-1].get("ultrasound")
                    and not cow.reproduction[-1].get("calving")):

                cow.reproduction[-1] = CowUtils.set_reproduction(
                    user_id,
                    cow.reproduction[-1])

        db.session.commit()
        lg.info("reproduction reload")

    @staticmethod
    def get_valid_reproduction(user_id : int) -> dict[int, Reproduction]:
        """Récupère la dernière entrée de reproduction valide pour toutes les
        vaches dont les ultrasons ont été confirmés.

        Cette fonction renvoie un dictionnaire associant l'identifiant de chaque
        vache à leur reproduction la plus récente où les ultrasons ont été
        confirmés.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * dict[int, Reproduction]: Un dictionnaire d'identifiant de vaches
            contenant leur plus récente reproduction avec ultrasons confirmés
        """
        from .fonction import last
        cows: list[Cow] = Cow.query.filter_by(user_id=user_id, in_farm=True).all()
        return {
            cow.cow_id: cow.reproduction[-1]
            for cow in cows
            if last(cow.reproduction) and
                    cow.reproduction[-1].get("ultrasound") and
                    not cow.reproduction[-1].get("calving")
        }

    @staticmethod
    def validated_calving(cow_id: int, user_id : int, abortion: bool,
            info: str | None = None) -> None:
        """Valide le vêlage pour une vache et enregistre si c'était un
        avortement.

        Cette fonction met à jour la dernière reproduction de la vache spécifiée
        pour indiquer un vêlage, et enregistrer si c'était un avortement ou non.
        Si aucune vache n'est associée à l'identifiant fourni en argument, une
        erreur est marquée dans le journal et une ValueError est lancée.

        Arguments:
            * cow_id (int): Identifiant de la vache
            * user_id (int): Identifiant de l'utilisateur
            * abortion (bool): True si le vêlage était un avortement, False
            sinon
            * info (str | None): Notes et commentaires

        Lance:
            * ValueError si la vache n'existe pas
        """
        #TODO gestion pas d'insemination reproduction_ultrasound calving
        #TODO getstion info
        cow: Cow | None
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
        """Valide le tarissage d'une vache.

        Cette fonction met à jour l'historique de reproduction pour la vache
        associée à l'identifiant fourni en argument pour indiquer que la période
        de tarissage est terminée. Si la vache n'existe pas, une erreur est
        marquée dans le journal et une ValueError est lancée.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Lance:
            * ValueError si aucune vache ne correspond à l'identifiant fourni
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")

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
        """Valide la date de préparation du vêlage pour une vache.

        Cette fonction met à jour la dernière entrée de l'historique de
        reproduction de la vache associée à l'identifiant fourni en argument
        pour indiquer que la préparation au vêlage a bien été effectuée. Si la
        vache spécifiée n'existe pas, une erreur est marquée dans le journal et
        une ValueError est lancée.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
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
        """Met à jour une entrée de reproduction d'une vache.

        Cette fonction remplace l'entrée de reproduction à l'indice fourni en
        argument par un nouveau dictionnaire de reproduction, et enregistre
        (commit) le changement dans la base de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * repro_index (int): Indice de l'entrée dans l'historique
            * new_repro (Reproduction): Entrée de reproduction à insérer dans
            l'historique
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            cow.reproduction[repro_index] = new_repro
            db.session.commit()
            lg.info(f"{cow_id} : reproduction updated in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    @staticmethod
    def delete_cow_reproduction(user_id: int, cow_id: int, repro_index: int) -> None:
        """Supprime une entrée de l'historique de reproduction d'une vache.

        Cette fonction supprime l'entrée présente à l'indice fourni de
        l'historique de reproduction de la vache et enregistre (commit) les
        changements dans la base de données. Si la vache spécifiée n'existe pas,
        une erreur est marquée dans le journal et une ValueError est lancée.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * repro_index (int): Indice dans l'historique de l'entrée à
            supprimer

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id' : cow_id, 'user_id' : user_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            del cow.reproduction[repro_index]
            db.session.commit()
            lg.info(f"{cow_id} : reproduction deleted in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    # END reproduction functions ------------------------------------------------


# END COW FONCTION


# PRESCRIPTION FONCTION
class PrescriptionUtils:
    """Cette class est un namespace, tous ses membres sont statiques.

    Ce namespace regroupe les fonctions pour ajouter, retirer, récupérer et
    modifier les prescriptions et produits médicaux dans la base de données.
    """

    @staticmethod
    def add_prescription(user_id: int, date: date, care_items: dict[str, int]) -> None:
        """Ajoute une nouvelle prescription à la base de données avec les date
        et éléments spécifiés.

        Cette fonction créée un nouvel objet Prescription, l'ajoute à la base
        de données et enregistre (commit) les changements dans la base de
        données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * date (date): Date de la prescription
            * care_items (dict[str, int]): Éléments de la prescription,
            typiquement nom du traitement et dose
        """
        prescription = Prescription(user_id=user_id, date=date, care=care_items,
                dlc_left=False)  # type: ignore
        db.session.add(prescription)
        db.session.commit()

    @staticmethod
    def add_dlc_left(user_id: int, date: date, care_items: dict[str, int]) -> None:
        """Ajoute une prescription remisée pour péremption.

        Cette fonction créée un nouvel objet Prescription avec le flag DLC à
        True, l'ajoute à la base de donnée, et enregistre (commit) la
        transaction.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * date (date): Date de retrait du traitement
            * care_items (dict[str, int]): Éléments de la prescription,
            typiquement nom du traitement et dose
        """
        prescription = Prescription(user_id=user_id, date=date, care=care_items,
            dlc_left=True) # type: ignore
        db.session.add(prescription)
        db.session.commit()

    @staticmethod
    def get_all_prescriptions(user_id: int) -> list[Prescription]:
        """Récupère toutes les prescriptions de la base de données.

        Cette fonction récupère toutes les prescriptions présentes dans la base
        de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * list[Prescription]: Une liste des prescriptions présentes dans la
            base de données
        """
        return Prescription.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_all_prescriptions_cares(user_id: int) -> list[tuple[date, dict[str, int], bool]]:
        """Récupère toutes les prescriptions dans la base de données triées par
        ordre décroissant de date.

        Cette fonction collecte toutes les prescriptions présentes dans la base
        de données, retire la première entrée (l'en-tête), et renvoie les
        entrées ainsi collectées triées par date, en commençant par la plus
        récente.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * list[tuple[date, dict[str, int], bool]]: Liste des prescriptions
            présentes dans la base de données, par ordre décroissante de date.
        """

        all_cares: list[tuple[date, dict[str, int], bool]] = [
            (prescription.date, prescription.care, prescription.dlc_left)
            for prescription in (Prescription.query.filter_by(user_id=user_id).all())
        ]
        _ = all_cares.pop(0)  # suprimer l'entete
        # Tri décroissant sur la date
        all_cares.sort(key=lambda x: x[0], reverse=True)
        return all_cares

    @staticmethod
    def get_year_prescription(user_id : int, year: int) -> list[Prescription]:
        """Récupère toutes les prescriptions de la base de données datées d'une
        année spécifique.

        Cette fonction renvoie une liste des prescriptions présentes dans la
        base de données datées d'une certaine année.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année des prescriptions

        Renvoie:
            * list[Prescriptions]: Liste des prescriptions datées de l'année
            spécifiée
        """
        return Prescription.query.filter_by(user_id=user_id, dlc_left=False).filter(
            (extract("year", Prescription.date) == year) # type: ignore
        ).all()

    @staticmethod
    def get_dlc_left_on_year(user_id: int, year: int) -> list[Prescription]:
        """Récupère toutes les prescriptions pour lesquelles un traitement a été
        retiré car arrivé à expiration lors de l'année fournie en argument.

        Cette fonction récupère les prescriptions dans la base de données, les
        filtre pour correspondre à l'année fournie en argument, et renvoie
        celles qui ont expiré.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année au cours de laquelle les traitements sont
            arrivés à expiration

        Renvoie:
            * list[Prescription]: La liste des prescriptions dont le traitement
            a expiré au cours de l'année spécifiée
        """
        return Prescription.query.filter_by(user_id=user_id, dlc_left=True).filter(
            (extract("year", Prescription.date) == year) # type: ignore
        ).all()


# END PRESCRIPTION FONCTION


# PHARMACIE FONCTION
class PharmacieUtils:
    """Cette classe est un namespace, ses membres sont statiques.

    Ce namespace regroupe les fonctions pour récupérer, modifier et créer des
    entrées de pharmacie pour les années spécifiées, ainsi que gérer les stocks
    et usages de médicaments.
    """

    @staticmethod
    def get_pharmacie_year(user_id: int, year: int) -> Pharmacie:
        """Récupère l'entrée de pharmacie pour une année spécifique.

        Cette fonction renvoie l'objet Pharmacie pour l'année fournie en
        argument si une telle entrée existe, ValueError sinon.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année des entrées de pharmacie à récupérer

        Renvoie:
            * Pharmacie: l'entrée de Pharmacie pour l'année fournie en argument.

        Lance:
            * ValueError s'il n'existe pas d'entrée de pharmacie pour l'année
            spécifiée.
        """
        if pharmacie := Pharmacie.query.get({"user_id" : user_id, "year" : year }):
            return pharmacie
        raise ValueError(f"{year} doesn't exist.")

    @staticmethod
    def updateOrDefault_pharmacie_year(user_id: int, year: int,
            default: Pharmacie) -> Pharmacie:
        """Met à jour l'année de pharmacie correspondant à une année spécifiée
        si elle existe, sinon la créée avec les valeurs par défaut.

        Cette fonction met à jour tous les attributs de l'entrée de pharmacie
        correspondant à l'année fournie en argument, ou créée une nouvelle
        entrée remplie avec les valeurs par défaut fournies en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année de l'entrée à modifier
            * default (Pharmacie): Valeurs par défaut de l'entrée

        Renvoie:
            * Pharmacie: L'entrée modifiée ou créée pour l'année spécifiée
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
    def get_all_pharmacie(user_id: int) -> list[Pharmacie]:
        """Récupère toutes les entrées de pharmacie de la base de données.

        Cette fonction interroge la base de données et renvoie une liste de
        toutes les entrées Pharmacie qu'elle contient.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * list[Pharmacie]: La liste de toutes les entrées de pharmacie de la
            base de données
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
        """Créée et enregistre une nouvelle entrée de pharmacie pour une année
        spécifique, en utilisant les informations fournies en argument.

        Cette fonction construit un nouvel objet Pharmacie contenant les données
        fournies et enregistre (commit) les changements dans la base de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année de l'entrée de pharmacie
            * total_enter (dict[str, int]): Dictionnaire associant les noms et
            quantités de traitements ajoutés à la pharmacie au cours de l'année
            * total_used (dict[str, int]): Dictionnaire associant les noms et
            quantités de traitements utilisés au cours de l'année
            * total_out_dlc (dict[str, int]): Dictionnaire associant les noms et
            quantités de traitements expirés dans la pharmacie au cours de
            l'année
            * total_out (dict[str, int]): Dictionnaire associant les noms et
            quantités de traitements retirés de la pharmacie au cours de l'année
            * remaining_stock (dict[str, int]): Dictionnaire associant les noms
            et quantités de traitements restant à la fin de l'année
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
        """Créée et enregistre une nouvelle entrée de pharmacie, pour l'année
        spécifiée, avec les stocks restants spécifiés.

        Cette fonction ajoute un nouvel objet Pharmacie pour l'année fournie en
        argument, vierge à l'exception des stocks restants fournis en argument.
        Si une entrée de pharmacie existe déjà pour l'année spécifiée, lance une
        ValueError.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année de la nouvelle entrée de pharmacie
            * remaining_stock (dict[str, int]): Dictionnaire associant les noms
            et quantités de traitements restant en stock

        Lance:
            * ValueError s'il existe déjà une entrée de pharmacie pour l'année
            spécifiée
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
    """Cette classe est un namespace, ses membres sont statiques.

    Ce namespace regroupe les fonctions de gestion (ajout, suppression,
    modification des paramètres) des utilisateurs et de récupération des
    réglages utilisateurs dans la base de données.
    """

    @staticmethod
    def add_user(email : str, password : str) -> None:
        """Ajoute un nouvel utilisateur à la base de données avec les données
        par défaut.

        Cette fonction créée un nouvel utilisateur en utilisant l'adresse e-mail
        et le mot de passe fournis en argument, avec les durées de tarissement
        et de préparation du vêlage par défaut.

        Arguments:
            * email (str): Adresse e-mail du nouvel utilisateur
            * password (str): Mot de passe du nouvel utilisateur
        """

        user = Users(email=email, password=password, setting={"dry_time": 0, "calving_preparation_time": 0})
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def set_user_setting(user_id : int, dry_time: int, calving_preparation: int) -> None:
        """Met à jour les réglages utilisateur concernant les durées de
        tarissement et de préparation du vêlage.

        Cette fonction met à jour les durées de tarissement et de préparation
        du vêlage pour l'utilisateur associé à l'identifiant fourni en argument,
        et enregistre (commit) les changements dans la base de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * dry_time (int): Durée de tarissement
            * calving_preparation (int): Durée de préparation au vêlage
        """

        user: Users = Users.query.get(user_id) # type: ignore
        user.setting["dry_time"] = dry_time # type: ignore
        user.setting["calving_preparation_time"] = calving_preparation # type: ignore
        db.session.commit()

    @staticmethod
    def get_user_setting(user_id : int) -> Setting:
        """Récupère les réglages utilisateur de durée de tarissement et de
        préparation au vêlage

        Cette fonction retourne le dictionnaire des réglages de l'utilisateur
        associé à l'identidiant fourni en argument concernant les durées de
        tarissement et de préparation au vêlage.

        Renvoie:
            * Settings: les réglages utilisateur de durée de tarissement et de
            préparation au vêlage
        """
        user: Users = Users.query.get(user_id) # type: ignore
        return user.setting # type: ignore

    @staticmethod
    def get_user(user_id: int) -> Users:
        """Récupère l'utilisateur associé à l'identifiant fourni en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
        """
        if user := Users.query.get(user_id):
            return user
        else:
            raise #TODO raise get_user mais peut etre pas apparament bug

    @staticmethod
    def add_medic_in_pharma_list(user_id: int, medic: str, mesur: int) -> None:
        """Ajoute un médicament à la pharmacie.

        Cette fonction ajoute un médicament à la pharmacie de l'utilisateur s'il
        n'existe pas déjà. S'il existe déjà, une erreur est marquée dans le
        journal.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * medic (str): Nom du médicament
            * mesur (int): Quantité de médicament
        """
        user: Users = Users.query.get(user_id) # type: ignore
        user.medic_list.setdefault(medic,mesur)
        db.session.commit()
        lg.info(f"{medic} add in pharma list")


    @staticmethod
    def get_pharma_list(user_id: int) -> list[str]:
        """Récupère la liste des médicaments dans la pharmacie de l'utilisateur.

        Cette fonction renvoie un dictionnaire contenant les médicaments
        présents dans la pharmacie de l'utilisateur ainsi que leurs quantité.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * dict[str, int]: Un dictionnaire associant les noms des médicaments
            à leurs quantités
        """
        user : Users = Users.query.get(user_id) # type: ignore
        return user.medic_list # type: ignore

# END USERS FONCTION
