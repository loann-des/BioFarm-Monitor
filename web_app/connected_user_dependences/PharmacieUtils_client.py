from typing import TypedDict


from ..models import Pharmacie, PharmacieUtils

import web_app.connected_user as Connected_user
import json

class Medicament_Quantite(TypedDict):
    """Dictionnaire associant les noms de traitements et leurs quantités."""
    name: str
    quantity: int


class PharmacieClient:

    year: int
    """Année de l'entrée de pharmacie"""

    total_enter: Medicament_Quantite | None
    """Quantité de médicaments ajoutés à la pharmacie durant l'année. """

    total_used: Medicament_Quantite | None
    """Quantité de médicaments utilisés durant l'année. """

    total_used_calf: Medicament_Quantite | None
    """Quantité de médicaments utilisés pour les veaux durant l'année. """

    total_out_dlc: Medicament_Quantite | None
    """Quantité de médicaments retirés de la pharmacie durant l'année pour cause de DLC dépassée. """

    total_out: Medicament_Quantite | None
    """Quantité de médicaments retirés de la pharmacie durant l'année pour cause de DLC et utilisation . """

    remaining_stock: Medicament_Quantite | None
    """Quantité de médicaments restant en stock à la fin de l'année. """

    def __init__(self, year: int,
                remaining_stock: Medicament_Quantite,
                 total_enter: Medicament_Quantite | None = None,
                 total_used: Medicament_Quantite | None = None,
                 total_used_calf: Medicament_Quantite | None = None,
                 total_out_dlc: Medicament_Quantite | None = None,
                 total_out: Medicament_Quantite | None = None
                 ) -> None:
        self.year = year
        self.total_enter = total_enter
        self.total_used = total_used
        self.total_used_calf = total_used_calf
        self.total_out_dlc = total_out_dlc
        self.total_out = total_out
        self.remaining_stock = remaining_stock

    def to_pharmacie_json(self) -> str:
        """Convertit l'objet PharmacieClient en une chaîne JSON.

        Cette fonction convertit les attributs de l'objet PharmacieClient en un format JSON, en utilisant les noms d'attributs correspondants de la classe Pharmacie.

        Renvoie:
            * str: Chaîne JSON représentant l'objet PharmacieClient.
        """
        pharmacie_dict = {
            "id": self.year,
            "year": self.year,
            "total_enter": self.total_enter,
            "total_used": self.total_used,
            "total_used_calf": self.total_used_calf,
            "total_out_dlc": self.total_out_dlc,
            "total_out": self.total_out,
            "remaining_stock": self.remaining_stock
        }
        return json.dumps(pharmacie_dict)

class PharmacieUtils_client:
    connected_user: Connected_user.ConnectedUser
    """L'utilisateur connecté associé à ce client utils"""

    list_pharmacie: list[PharmacieClient]
    """Liste de toutes les entrées de pharmacie de la base de données associées à l'utilisateur connecté, chacune correspondant à une année différente. """

    def __init__(self, user_id: int) -> None:
        pharmacies_list = PharmacieUtils.get_all_pharmacie(user_id)
        self.list_pharmacie = [PharmacieClient(year=pharmacy.year,
                                               total_enter=pharmacy.total_enter,
                                               total_used=pharmacy.total_used,
                                               total_used_calf=pharmacy.total_used_calf,
                                               total_out_dlc=pharmacy.total_out_dlc,
                                               total_out=pharmacy.total_out,
                                               remaining_stock=pharmacy.remaining_stock)
                               for pharmacy in pharmacies_list]

    def get_pharmacie_year(self, year: int) -> PharmacieClient:
        """Récupère l'entrée de pharmacie pour une année spécifique.

        Cette fonction renvoie l'objet PharmacieClient pour l'année fournie en
        argument si une telle entrée existe, ValueError sinon.

        Arguments:
            * year (int): Année des entrées de pharmacie à récupérer

        Renvoie:
            * PharmacieClient: l'entrée de PharmacieClient pour l'année fournie en argument.

        Lance:
            * ValueError s'il n'existe pas d'entrée de pharmacie pour l'année
            spécifiée.
        """
        for pharmacie in self.list_pharmacie:
            if pharmacie.year == year:
                return pharmacie
        raise ValueError(f"{year} doesn't exist.")

    def updateOrDefault_pharmacie_year(self, year: int,
                                       default: PharmacieClient) -> PharmacieClient:
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
            * PharmacieClient: L'entrée modifiée ou créée pour l'année spécifiée
        """

        if pharmacie := self.get_pharmacie_year(year):
            for attr in default.__dict__:
                if not attr.startswith("_") and hasattr(pharmacie, attr):
                    setattr(pharmacie, attr, getattr(default, attr))
        else:
            self.list_pharmacie.append(default)
            pharmacie = default

        PharmacieUtils.updateOrDefault_pharmacie_year(
            user_id=self.connected_user.id,
            year=pharmacie.year,
            # TODO gestion formating pharmacie client -> pharmacie # type: ignore
            default=pharmacie.to_pharmacie()
        )
        return pharmacie

    def get_all_pharmacie(self) -> list[PharmacieClient]:
        """Récupère toutes les entrées de pharmacie associées à l'utilisateur connecté.

        Cette fonction renvoie une liste de toutes les entrées de pharmacie de la base de données associées à l'utilisateur connecté, chacune correspondant à une année différente.

        Renvoie:
            * list[PharmacieClient]: Liste de toutes les entrées de pharmacie de l'utilisateur connecté.
        """
        return self.list_pharmacie

    def set_pharmacie_year(
        self,
        year: int,
        remaining_stock: Medicament_Quantite,
        total_enter: Medicament_Quantite | None = None,
        total_used: Medicament_Quantite | None = None,
        total_used_calf: Medicament_Quantite | None = None,
        total_out_dlc: Medicament_Quantite | None = None,
        total_out: Medicament_Quantite | None = None,
    ) -> None:
        """Créée et enregistre une nouvelle entrée de pharmacie pour une année
        spécifique, en utilisant les informations fournies en argument.

        Cette fonction construit un nouvel objet Pharmacie contenant les données
        fournies et enregistre (commit) les changements dans la base de données.

        Arguments:
            * year (int): Année de l'entrée de pharmacie
            * total_enter (Medicament_Quantite): Dictionnaire associant les noms et
            quantités de traitements ajoutés à la pharmacie au cours de l'année
            * total_used (Medicament_Quantite): Dictionnaire associant les noms et
            quantités de traitements utilisés au cours de l'année
            * total_used_calf (Medicament_Quantite): Dictionnaire associant les noms et
            quantités de traitements utilisés pour les vaches au cours de l'année
            * total_out_dlc (Medicament_Quantite): Dictionnaire associant les noms et
            quantités de traitements expirés dans la pharmacie au cours de
            l'année
            * total_out (Medicament_Quantite): Dictionnaire associant les noms et
            quantités de traitements retirés de la pharmacie au cours de l'année
            * remaining_stock (Medicament_Quantite): Dictionnaire associant les noms
            et quantités de traitements restant à la fin de l'année
        """

        pharmacie_client = PharmacieClient(
            year=year,
            total_enter=total_enter,
            total_used=total_used,
            total_used_calf=total_used_calf,
            total_out_dlc=total_out_dlc,
            total_out=total_out,
            remaining_stock=remaining_stock
        )

        pharmacie = Pharmacie(
            user_id=self.connected_user.id,
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
        if Pharmacie.query.get({"user_id": user_id, "year": year}):
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
