from typing import TYPE_CHECKING, TypedDict

from web_app.fonction import my_strftime

from ..models import Prescription, PrescriptionUtils
from datetime import date, datetime
from PharmacieUtils_client import PharmacieClientAttr

class Prescription_export_format(TypedDict):
    """Représente une prescription avec une date associée.

    :var date_prescription: str, Date de la prescription au format 'YYYY-MM-DD'
    :var prescription: dict[str, int], Dictionnaire des médicaments et dosages prescrits
    :var dlc_left: bool, True si la date de consommation est atteinte, False sinon.
    """
    date_prescription: str  # date au format 'YYYY-MM-DD'
    prescription: dict[str, int]  # [medicament,dosage]
    # True si la date de consommation est atteinte, False sinon.
    dlc_left: bool


class PrescriptionClient:
    from datetime import date as dateType
    date: dateType
    care: dict[str, int]
    dlc_left: bool

    def __init__(self, date: dateType, care: dict[str, int], dlc_left: bool):
        self.date = date
        self.care = care
        self.dlc_left = dlc_left
        
    def to_prescription_db(self, user_id: int) -> Prescription: #TODO retirer au passage a l'api
        """Convertit l'objet PrescriptionClient en un objet Prescription pour la
        base de données.

        Cette fonction prend les attributs de l'objet PrescriptionClient et les
        utilise pour créer un nouvel objet Prescription qui peut être stocké
        dans la base de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur auquel la prescription
            est associée

        Renvoie:
            * Prescription: Un objet Prescription prêt à être ajouté à la base
            de données
        """
        return Prescription(user_id=user_id, date=self.date, care=self.care, dlc_left=self.dlc_left)


class PrescriptionUtilsClient:
    if TYPE_CHECKING:
        from connected_user import ConnectedUser

    connected_user: "ConnectedUser"
    list_prescriptions: list[PrescriptionClient]

    def __init__(self, connected_user: "ConnectedUser"):
        self.connected_user = connected_user
        list_prescriptions_db = PrescriptionUtils.get_all_prescriptions(
            user_id=connected_user.id)
        self.list_prescriptions = [PrescriptionClient(date=prescription.date,
                                                      care=prescription.care,
                                                      dlc_left=prescription.dlc_left)
                                   for prescription in list_prescriptions_db]

    def add_prescription(self, date: date, care_items: dict[str, int]) -> None:
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
        prescription : PrescriptionClient = PrescriptionClient(date=date, care=care_items, dlc_left=False)
        PrescriptionUtils.add_prescription(user_id=self.connected_user.id, date=date, care_items=care_items)#TODO remplaser au passage a l'api
        # if request.status :
        self.list_prescriptions.append(prescription)
        self.connected_user.pharmacie_utils_client.modify_pharmacie_year(
            year=datetime.now().year,
            attr=PharmacieClientAttr.total_used,
            stock=care_items)
        
    def add_dlc_left(self, date: date, care_items: dict[str, int]) -> None:
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
        if not self.connected_user.pharmacie_utils_client.verify_pharmacie_out(year=datetime.now().year, stock=care_items) :
            raise ValueError("Stock insuffisant pour retirer le traitement")
            
        prescription = PrescriptionClient(date=date, care=care_items, dlc_left=True)
        PrescriptionUtils.add_dlc_left(user_id=self.connected_user.id, date=date, care_items=care_items) #TODO remplaser au passage a l'api
        
        # if request.status :
        self.connected_user.pharmacie_utils_client.modify_pharmacie_year(
            year=datetime.now().year,
            attr=PharmacieClientAttr.total_out_dlc,
            stock=care_items)
        self.list_prescriptions.append(prescription)

    def get_all_prescriptions(self) -> list[PrescriptionClient]:
        """Récupère toutes les prescriptions de la base de données.

        Cette fonction récupère toutes les prescriptions présentes dans la base
        de données.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * list[Prescription]: Une liste des prescriptions présentes dans la
            base de données
        """
        return self.list_prescriptions

    def get_all_prescriptions_cares(self) -> list[Prescription_export_format]:
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
            Prescription_export_format(date_prescription=my_strftime(prescription.date),
                                       prescription=prescription.care,
                                       dlc_left=prescription.dlc_left)
            for prescription in self.list_prescriptions
            ]
        # Tri décroissant sur la date
        all_cares.sort(key=lambda x: x["date_prescription"], reverse=True)
        return all_cares

    def get_year_prescription(self, year: int) -> list[PrescriptionClient]:
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
        
        return list(filter(lambda e: ((not e.dlc_left) and e.date.year == year) , self.list_prescriptions))

    def get_dlc_left_on_year(self ,year: int) -> list[PrescriptionClient]:
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
        return list(filter(lambda e: (e.dlc_left and e.date.year == year) , self.list_prescriptions))

    
