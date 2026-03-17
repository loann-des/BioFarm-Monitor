import logging as lg

from datetime import date
from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    JSON,
    extract)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from web_app.models.type_dict import Prescription_export_format

from .. import db

class Prescription(db.Model):
    """Représente un traitement dans la base de données. Sont inclus la date de
    prescription, le contenu du traitement, et la date limite de consommation.
    """
    from datetime import date as dateType

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    """Identifiant du traitement."""

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"),
                                         nullable=False)

    date: Mapped[dateType] = mapped_column(Date, nullable=False)
    """Date de la prescription."""

    # Traitement stocké au format JSON en base
    care: Mapped[dict[str, int]] = mapped_column(MutableDict.as_mutable(JSON),
                                                 default=dict, nullable=False)
    """Informations sur le traitement, stocké au format JSON dans la base de
    données."""

    dlc_left: Mapped[bool] = mapped_column(Boolean)
    """True si remiser pour date limite de consommation est dépassée, False sinon."""

    # TODO ajouter le pdf de la prescription scanné ?

    def __init__(self,
                 user_id: int,
                 date: dateType,
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
        prescription = Prescription(user_id=user_id, date=date, care=care_items,  # type: ignore
                                    dlc_left=False)
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
        # TODO Pas plus de sortie= que de qt en stock
        prescription = Prescription(user_id=user_id, date=date, care=care_items,  # type: ignore
                                    dlc_left=True)
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
    def get_all_prescriptions_cares(user_id: int) -> list[Prescription_export_format]:
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
        all_cares: list[Prescription_export_format] = [
            Prescription_export_format(date_prescription=prescription.date,
                                       prescription=prescription.care,
                                       dlc_left=prescription.dlc_left)
            for prescription in (Prescription.query.filter_by(user_id=user_id).all())
        ]
        # Tri décroissant sur la date
        all_cares.sort(key=lambda x: x["date_prescription"], reverse=True)
        return all_cares

    @staticmethod
    def get_year_prescription(user_id: int, year: int) -> list[Prescription]:
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
            (extract("year", Prescription.date) == year)  # type: ignore
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
            (extract("year", Prescription.date) == year)  # type: ignore
        ).all()

