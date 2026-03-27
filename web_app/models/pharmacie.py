# Standard
from collections import Counter
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    JSON,
    )
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column
from typing import Any

from .. import db

class PharmacieAttr(Enum):
    total_enter = "total_enter"
    total_used = "total_used"
    total_used_calf = "total_used_calf"
    total_out_dlc = "total_out_dlc"
    remaining_stock = "remaining_stock"


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
        user_id: int,
        year: int,
        remaining_stock: dict[str, int],
        total_enter: dict[str, int],
        total_used: dict[str, int],
        total_used_calf: dict[str, int],
        total_out_dlc: dict[str, int],
        total_out: dict[str, int]
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
        if pharmacie := Pharmacie.query.get({"user_id": user_id, "year": year}):
            return pharmacie
        raise ValueError(f"{year} doesn't exist.")

    @staticmethod
    def updateOrDefault_pharmacie_year(user_id: int,
                                       default: Pharmacie) -> Pharmacie:
        """Met à jour ou crée une entrée de pharmacie pour une année donnée.

        Cette fonction cherche une entrée de pharmacie pour l'utilisateur et
        l'année de l'objet fourni, met à jour tous ses attributs connus avec
        ceux de l'objet `default` si elle existe, ou ajoute une nouvelle entrée
        sinon, puis enregistre les changements en base.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur concerné
            * default (Pharmacie): Objet de référence contenant les valeurs à
            appliquer ou à insérer

        Renvoie:
            * Pharmacie: L'entrée de pharmacie mise à jour ou nouvellement
            créée.
        """
        year = default.year
        pharmacie_db = Pharmacie.query.get({"user_id": user_id, "year": year})

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
            * total_enter (dict[str,int]): Dictionnaire associant les noms et
            quantités de traitements ajoutés à la pharmacie au cours de l'année
            * total_used (dict[str,int]): Dictionnaire associant les noms et
            quantités de traitements utilisés au cours de l'année
            * total_out_dlc (dict[str,int]): Dictionnaire associant les noms et
            quantités de traitements expirés dans la pharmacie au cours de
            l'année
            * total_out (dict[str,int]): Dictionnaire associant les noms et
            quantités de traitements retirés de la pharmacie au cours de l'année
            * remaining_stock (dict[str,int]): Dictionnaire associant les noms
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
            * remaining_stock (dict[str,int]): Dictionnaire associant les noms
            et quantités de traitements restant en stock

        Lance:
            * ValueError s'il existe déjà une entrée de pharmacie pour l'année
            spécifiée
        """
        if Pharmacie.query.get({"user_id": user_id, "year": year}):
            raise ValueError(f"{year} already existe.")

        pharmacie = Pharmacie(
            user_id=user_id,
            year=year,
            remaining_stock=remaining_stock,
            total_enter={},
            total_used={},
            total_used_calf={},
            total_out_dlc={},
            total_out={},
        )
        db.session.add(pharmacie)
        db.session.commit()

    @staticmethod
    def modify_pharmacie_year(user_id: int, year: int, attr: PharmacieAttr, care_delta: dict[str, int]) -> None:
        """Modifie une entrée de pharmacie pour une année spécifique, en
        mettant à jour un attribut spécifique avec les données fournies.

        Cette fonction met à jour l'attribut de l'entrée de pharmacie
        correspondant à l'année fournie en argument, avec les données fournies
        en argument. Et met à jour les attributs "total_out" et "remaining_stock" en conséquence.
        commit les changements dans la base de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année de l'entrée de pharmacie à modifier
            * attr (str): Attribut de l'entrée de pharmacie à modifier, parmi
            "total_enter", "total_used", "total_used_calf", "total_out_dlc"
        """
        pharmacie : Pharmacie = PharmacieUtils.get_pharmacie_year(user_id=user_id, year=year)
        remaining_stock_old = pharmacie.remaining_stock
        
        setattr(pharmacie, attr.value, dict(Counter(getattr(pharmacie, attr.value)) + Counter(care_delta)))
        
        if attr in [PharmacieAttr.total_used, PharmacieAttr.total_used_calf, PharmacieAttr.total_out_dlc]:
            pharmacie.total_out = dict(Counter(pharmacie.total_out) + Counter(care_delta)) # on met a jour le total out si c'est du used ou du out dlc
            if attr == PharmacieAttr.total_used_calf:
                pharmacie.total_used = dict(Counter(pharmacie.total_used) + Counter(care_delta)) # on met a jour le total used si c'est du used calf
            pharmacie.remaining_stock = dict(Counter(pharmacie.remaining_stock) - Counter(care_delta)) # on retire du stock restant si c'est du used ou du out dlc
        if attr == PharmacieAttr.total_enter:
            pharmacie.remaining_stock = dict(Counter(pharmacie.remaining_stock) + Counter(care_delta)) # on ajoute au stock restant si c'est du total enter
        
        db.session.commit()
        if year < datetime.now().year :
            #propagation de la modification sur remaining stock des années suivante
            stock_delta = dict(Counter(pharmacie.remaining_stock) - Counter(remaining_stock_old))
            PharmacieUtils.modify_pharmacie_year(user_id=user_id, year=year+1, attr= PharmacieAttr.remaining_stock, care_delta=stock_delta)
        
    @staticmethod
    def validat_quantity(user_id: int, stock_delta: dict[str, int], year_to_verify: int) -> bool:
        for year in range(year_to_verify,datetime.now().year):
            pharmatcie: Pharmacie = PharmacieUtils.get_pharmacie_year(user_id=user_id, year=year)
            new_remaining_stock : dict[str, int] =  dict(Counter(pharmatcie.remaining_stock) + Counter(stock_delta) )
            if any(x < 0 for x in new_remaining_stock.values()) :
                return False
        return True
            
