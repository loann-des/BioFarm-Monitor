from collections import Counter
from enum import Enum
from typing import TYPE_CHECKING

from ..models import Pharmacie, PharmacieUtils

class PharmacieClientAttr(Enum):
    total_enter = "total_enter"
    total_used = "total_used"
    total_used_calf = "total_used_calf"
    total_out_dlc = "total_out_dlc"
    


class PharmacieClient:  #TODO e revoir a l'utilisation de mashmallow pour eviter d'avoir a faire cette classe
    """ Représente une entrée de pharmacie pour une année spécifique,
    avec les quantités de médicaments entrés, utilisés, sortis et restants en stock.
    
     :var year: int, Année de l'entrée de pharmacie
     :var total_enter: dict[str, int], Quantité de médicaments ajoutés à la pharmacie durant l'année.
     :var total_used: dict[str, int], Quantité de médicaments utilisés durant l'année.
     :var total_used_calf: dict[str, int], Quantité de médicaments utilisés pour les veaux durant l'année.
     :var total_out_dlc: dict[str, int], Quantité de médicaments retirés de la pharmacie durant l'année pour cause de DLC dépassée.
     :var total_out: dict[str, int], Quantité de médicaments retirés de la pharmacie durant l'année pour cause de DLC et utilisation.
     :var remaining_stock: dict[str, int], Quantité de médicaments restant en stock à la fin de l'année.
    """
    
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
        # TODO ne plus utiliser cette fonction au passage a l'api et gerer avec mashmallow


class PharmacieUtilsClient:
    """Gère les entrées de pharmacie côté client pour un utilisateur connecté.

    Cette classe fournit des méthodes pour récupérer, créer, modifier et vérifier
    les données de pharmacie d'un utilisateur au fil des années, en synchronisation
    avec la base de données via PharmacieUtils.
    """
    if TYPE_CHECKING:
        from connected_user import ConnectedUser

    connected_user: "ConnectedUser"
    """L'utilisateur connecté associé à ce client utils"""

    list_pharmacie: list[PharmacieClient]
    """Liste de toutes les entrées de pharmacie de la base de données associées
    à l'utilisateur connecté, chacune correspondant à une année différente. """

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

    def find_pharmacie_year(self, year: int) -> PharmacieClient | None:
        """Recherche une entrée de pharmacie correspondant à une année spécifique.

        Cette fonction parcourt les entrées de pharmacie de l'utilisateur connecté et
        renvoie celle qui correspond à l'année fournie, ou None si aucune entrée n'existe pour cette année.

        Arguments:
            * year (int): Année de l'entrée de pharmacie à rechercher.

        Renvoie:
            * PharmacieClient | None: L'entrée de pharmacie correspondant à l'année spécifiée, ou None si aucune n'existe.
        """
        for pharmacie in self.list_pharmacie:
            if pharmacie.year == year:
                return pharmacie
        return None

    def get_pharmacie_year(self, year: int) -> PharmacieClient:
        """Récupère l'entrée de pharmacie correspondant à une année spécifique.

        Cette fonction parcourt les entrées de pharmacie de l'utilisateur connecté et
        renvoie celle qui correspond à l'année fournie, ou lève une erreur si aucune 
        entrée n'existe pour cette année.

        Arguments:
            * year (int): Année de l'entrée de pharmacie à récupérer.

        Renvoie:
            * PharmacieClient: L'entrée de pharmacie correspondant à l'année spécifiée.

        Lève:
            * ValueError: Si aucune entrée de pharmacie n'existe pour l'année spécifiée.
        """
        res = self.find_pharmacie_year(year)
        if res is None:
            raise ValueError(f"{year} doesn't exist.")
        return res

    def updateOrDefault_pharmacie_year(self,default: PharmacieClient) -> PharmacieClient:
        """Met à jour ou crée une entrée de pharmacie pour une année donnée.

        Cette fonction recherche une entrée de pharmacie correspondant à l'année
        fournie et met à jour ses attributs avec ceux de l'objet par défaut, ou crée une 
        nouvelle entrée si aucune n'existe, puis synchronise les données avec la base de données.

        Arguments:
            * year (int): Année de l'entrée de pharmacie à mettre à jour ou créer.
            * default (PharmacieClient): Objet contenant les données de pharmacie à appliquer pour l'année spécifiée.

        Renvoie:
            * PharmacieClient: L'entrée de pharmacie mise à jour ou nouvellement créée.
        """
       
        pharmacie = self.find_pharmacie_year(default.year)

        #TODO remplaser au passage a l'api
        
        status = PharmacieUtils.updateOrDefault_pharmacie_year( 
            user_id=self.connected_user.id,
            year=default.year, #TODO modifier dans models pour retiré année en argument et se baser uniquement sur le year de l'objet pharmacie client par defaut pour eviter les incohérences
            # TODO gestion formating pharmacie client -> pharmacie avec mashmallow # type: ignore
            default=default.to_pharmacie(self.connected_user.id)
        )
        
        if status:
            if pharmacie:
                for attr in default.__dict__:
                    if not attr.startswith("_") and hasattr(pharmacie, attr):
                        setattr(pharmacie, attr, getattr(default, attr))
            else:
                self.list_pharmacie.append(default)
                pharmacie = default

        return pharmacie or default # TODO a revoir

    def get_all_pharmacie(self) -> list[PharmacieClient]:
        """Récupère toutes les entrées de pharmacie associées à l'utilisateur connecté.

        Cette fonction renvoie une liste de toutes les entrées de pharmacie de la base de
        données associées à l'utilisateur connecté, chacune correspondant à une année différente.

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
        """Définit ou remplace les données de pharmacie pour une année spécifique.

        Cette fonction crée un objet PharmacieClient à partir des données fournies pour l'année donnée,
        puis l'enregistre ou le met à jour dans la liste des pharmacies de l'utilisateur et dans la base de données.

        Arguments:
            * year (int): Année de l'entrée de pharmacie à définir ou mettre à jour.
            * remaining_stock (dict[str, int]): Dictionnaire des stocks de médicaments restants en fin d'année.
            * total_enter (dict[str, int]): Dictionnaire des quantités de médicaments entrés dans la pharmacie durant l'année.
            * total_used (dict[str, int]): Dictionnaire des quantités de médicaments utilisées durant l'année.
            * total_used_calf (dict[str, int]): Dictionnaire des quantités de médicaments utilisés pour les veaux durant l'année.
            * total_out_dlc (dict[str, int]): Dictionnaire des quantités de médicaments retirés pour cause de DLC dépassée durant l'année.
            * total_out (dict[str, int]): Dictionnaire des quantités totales de médicaments retirés de la pharmacie durant l'année.
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
            default=pharmacie_client)

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

    def modify_pharmacie_year(self, year: int, attr: PharmacieClientAttr, stock: dict[str, int]) -> None:
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
        pharmacie : PharmacieClient = self.get_pharmacie_year(year)

        setattr(pharmacie, attr.value, dict(Counter(getattr(pharmacie, attr.value)) + Counter(stock)))
        
        if attr in [PharmacieClientAttr.total_used, PharmacieClientAttr.total_used_calf, PharmacieClientAttr.total_out_dlc]:
            pharmacie.total_out = dict(Counter(pharmacie.total_out) + Counter(stock)) # on met a jour le total out si c'est du used ou du out dlc
            if attr == PharmacieClientAttr.total_used_calf:
                pharmacie.total_used = dict(Counter(pharmacie.total_used) + Counter(stock)) # on met a jour le total used si c'est du used calf
            pharmacie.remaining_stock = dict(Counter(pharmacie.remaining_stock) - Counter(stock)) # on retire du stock restant si c'est du used ou du out dlc
        if attr == PharmacieClientAttr.total_enter:
            pharmacie.remaining_stock = dict(Counter(pharmacie.remaining_stock) + Counter(stock)) # on ajoute au stock restant si c'est du total enter
            
        PharmacieUtilsClient.updateOrDefault_pharmacie_year(
            self,
            default=pharmacie
        )
        
    def verify_pharmacie_out(self, year: int, stock: dict[str, int]) -> bool:
        """Vérifie si les quantités de médicaments à retirer de la pharmacie pour une année spécifique sont disponibles en stock.

        Cette fonction vérifie que les quantités de médicaments à retirer de la pharmacie pour l'année fournie en argument sont disponibles en stock
        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * year (int): Année de l'entrée de pharmacie à vérifier
            * stock (dict[str, int]): Dictionnaire associant les noms et quantités de traitements à retirer de la pharmacie
        """
        remaining_stock_year = self.get_pharmacie_year(year).remaining_stock
        remaining_stock_after_op = dict(Counter(remaining_stock_year) - Counter(stock))
        return all(quantity >= 0 for quantity in remaining_stock_after_op.values())
        
        