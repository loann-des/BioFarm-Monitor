# Standard
import logging as lg

from flask_login import UserMixin
from sqlalchemy import (
    Integer,
    String,
    JSON,
    )
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column
from typing import TypedDict, Any

from .. import db

class Setting(TypedDict):
    """Stocke des réglages utilisateur, en l'occurrence les durées de
    tarissement et de préparation au vêlage.

    :var dry_time: int, Temps de tarissement (en jour)
    :var calving_preparation_time: int, Temps de préparation au vêlage (en jour)
    """

    dry_time: int  # Temps de tarrisement (en jour)
    calving_preparation_time: int  # Temps de prepa vellage (en jour)

class Users(db.Model, UserMixin):
    """Représente un utilisateur dans la base de données. Inclut les durées de
    tarissement et de préparation du vêlage.

    Cette classe contient la configuration utilisateur de gestion des
    traitements et cycles reproductifs.
    """
    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True)  # numero utilisateur
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    setting: Mapped[Setting] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )  # setting utilisateur
    medic_list: Mapped[dict[Any, Any]] = mapped_column(MutableDict.as_mutable(JSON),
                                                       default=dict, nullable=False)

    def __init__(self, email: str, password: str, setting: Setting):
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


class UserUtils:
    """Cette classe est un namespace, ses membres sont statiques.

    Ce namespace regroupe les fonctions de gestion (ajout, suppression,
    modification des paramètres) des utilisateurs et de récupération des
    réglages utilisateurs dans la base de données.
    """

    @staticmethod
    def add_user(email: str, password: str) -> None:
        """Ajoute un nouvel utilisateur à la base de données avec les données
        par défaut.

        Cette fonction créée un nouvel utilisateur en utilisant l'adresse e-mail
        et le mot de passe fournis en argument, avec les durées de tarissement
        et de préparation du vêlage par défaut.

        Arguments:
            * email (str): Adresse e-mail du nouvel utilisateur
            * password (str): Mot de passe du nouvel utilisateur
        """

        user = Users(email=email, password=password, setting={
                     "dry_time": 0, "calving_preparation_time": 0})
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def set_user_setting(user_id: int, dry_time: int, calving_preparation: int) -> None:
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

        user: Users = Users.query.get(user_id)  # type: ignore
        user.setting["dry_time"] = dry_time  # type: ignore
        # type: ignore
        user.setting["calving_preparation_time"] = calving_preparation
        db.session.commit()

    @staticmethod
    def get_user_setting(user_id: int) -> Setting:
        """Récupère les réglages utilisateur de durée de tarissement et de
        préparation au vêlage

        Cette fonction retourne le dictionnaire des réglages de l'utilisateur
        associé à l'identidiant fourni en argument concernant les durées de
        tarissement et de préparation au vêlage.

        Renvoie:
            * Settings: les réglages utilisateur de durée de tarissement et de
            préparation au vêlage
        """
        user: Users = Users.query.get(user_id)  # type: ignore
        return user.setting  # type: ignore

    @staticmethod
    def get_user(user_id: int) -> Users:
        """Récupère l'utilisateur associé à l'identifiant fourni en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
        """
        return Users.query.get(user_id)  # type: ignore

    @staticmethod
    def add_medic_in_pharma_list(user_id: int, medic: str, mesur: str) -> None:
        """Ajoute un médicament à la pharmacie.

        Cette fonction ajoute un médicament à la pharmacie de l'utilisateur s'il
        n'existe pas déjà. S'il existe déjà, une erreur est marquée dans le
        journal.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * medic (str): Nom du médicament
            * mesur (int): Quantité de médicament
        """
        user: Users = Users.query.get(user_id)  # type: ignore
        user.medic_list.setdefault(medic, mesur)
        db.session.commit()
        lg.info(f"{medic} add in pharma list")

    @staticmethod
    def get_pharma_list(user_id: int) -> dict[str, int]:
        """Récupère la liste des médicaments dans la pharmacie de l'utilisateur.

        Cette fonction renvoie un dictionnaire contenant les médicaments
        présents dans la pharmacie de l'utilisateur ainsi que leurs quantité.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * dict[str, int]: Un dictionnaire associant les noms des médicaments
            à leurs quantités
        """
        user: Users = Users.query.get(user_id)  # type: ignore
        return user.medic_list  # type: ignore

# END USERS FONCTION
