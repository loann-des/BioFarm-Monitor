from typing import TYPE_CHECKING

from ..models import Pharmacie, PharmacieUtils


class PharmacieClient:

    year: int
    """Année de l'entrée de pharmacie"""

    total_enter: dict[str, int]
    """Quantité de médicaments ajoutés à la pharmacie durant l'année. """

    total_used: dict[str, int]
    """Quantité de médicaments utilisés durant l'année. """

    total_used_calf: dict[str, int]
    """Quantité de médicaments utilisés pour les veaux durant l'année. """

    total_out_dlc: dict[str, int]
    """Quantité de médicaments retirés de la pharmacie durant l'année pour cause de DLC dépassée. """

    total_out: dict[str, int]
    """Quantité de médicaments retirés de la pharmacie durant l'année pour cause de DLC et utilisation . """

    remaining_stock: dict[str, int]
    """Quantité de médicaments restant en stock à la fin de l'année. """

    def __init__(self, year: int,
                 remaining_stock: dict[str, int],
                 total_enter: dict[str, int] | None = None,
                 total_used: dict[str, int] | None = None,
                 total_used_calf: dict[str, int] | None = None,
                 total_out_dlc: dict[str, int] | None = None,
                 total_out: dict[str, int] | None = None
                 ) -> None:
        """Initialise un objet PharmacieClient pour une année donnée.

        Cette méthode configure les quantités totales entrées, utilisées, sorties et le stock restant pour l'année spécifiée.

        Arguments:
            * year (int): Année de l'entrée de pharmacie.
            * remaining_stock (dict[str,int]): Dictionnaire des médicaments restants en stock à la fin de l'année.
            * total_enter (dict[str,int] | None): Dictionnaire des quantités de médicaments entrés dans la pharmacie durant l'année.
            * total_used (dict[str,int] | None): Dictionnaire des quantités de médicaments utilisés durant l'année.
            * total_used_calf (dict[str,int] | None): Dictionnaire des quantités de médicaments utilisés pour les veaux durant l'année.
            * total_out_dlc (dict[str,int] | None): Dictionnaire des quantités de médicaments sortis pour cause de DLC dépassée durant l'année.
            * total_out (dict[str,int] | None): Dictionnaire des quantités totales de médicaments sortis de la pharmacie durant l'année.
        """
        self.year = year
        self.total_enter = total_enter or {}
        self.total_used = total_used or {}
        self.total_used_calf = total_used_calf or {}
        self.total_out_dlc = total_out_dlc or {}
        self.total_out = total_out or {}
        self.remaining_stock = remaining_stock

    def to_pharmacie(self, user_id: int) -> Pharmacie:
        """Convertit l'objet PharmacieClient en objet Pharmacie.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur associé à l'entrée de pharmacie

        Renvoie:
            * Pharmacie: L'entrée de pharmacie correspondante à l'objet PharmacieClient
        """
        return Pharmacie(
            user_id=user_id,
            year=self.year,
            total_enter=self.total_enter,
            total_used=self.total_used,
            total_used_calf=self.total_used_calf,
            total_out_dlc=self.total_out_dlc,
            total_out=self.total_out,
            remaining_stock=self.remaining_stock
        )
        # TODO ne plus utiliser cette fonction au passage a l'api et evoiyer le to_json directement a l'api


class PharmacieUtilsClient:
    if TYPE_CHECKING:
        from connected_user import ConnectedUser

    connected_user: "ConnectedUser"
    """L'utilisateur connecté associé à ce client utils"""

    list_pharmacie: list[PharmacieClient]
    """Liste de toutes les entrées de pharmacie de la base de données associées à l'utilisateur connecté, chacune correspondant à une année différente. """

    def __init__(self, connected_user: "ConnectedUser") -> None:
        self.connected_user = connected_user
        pharmacies_list = PharmacieUtils.get_all_pharmacie(
            user_id=self.connected_user.id)

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
        try:
            pharmacie = self.get_pharmacie_year(year)
        except ValueError:
            pharmacie = None

        if pharmacie:
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
            default=pharmacie.to_pharmacie(self.connected_user.id)
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
        remaining_stock: dict[str, int],
        total_enter: dict[str, int],
        total_used: dict[str, int],
        total_used_calf: dict[str, int],
        total_out_dlc: dict[str, int],
        total_out: dict[str, int],
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
        self.updateOrDefault_pharmacie_year(
            year=year, default=pharmacie_client)

        # TODO ne plus utiliser cette fonction au passage a l'api et evoiyer le to_json directement a l'api
        PharmacieUtils.set_pharmacie_year(
            user_id=self.connected_user.id,
            year=year,
            total_enter=total_enter,
            total_used=total_used,
            total_used_calf=total_used_calf,
            total_out_dlc=total_out_dlc,
            total_out=total_out,
            remaining_stock=remaining_stock
        )

    def upload_pharmacie_year(self, year: int, remaining_stock: dict[str, int]) -> None:
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
        try:
            pharmacie = self.get_pharmacie_year(year)
        except ValueError:
            pharmacie = None

        if pharmacie:
            raise ValueError(f"{year} already existe.")

        pharmacie = PharmacieClient(
            year=year,
            total_enter=None,
            total_used=None,
            total_used_calf=None,
            total_out_dlc=None,
            total_out=None,
            remaining_stock=remaining_stock,
        )
        self.list_pharmacie.append(pharmacie)

        # TODO ne plus utiliser cette fonction au passage a l'api et evoiyer le to_json directement a l'api
        PharmacieUtils.upload_pharmacie_year(
            user_id=self.connected_user.id,
            year=year,
            remaining_stock=remaining_stock
        )
