from collections import Counter
from typing import TYPE_CHECKING

from web_app.fonction import my_strftime

from datetime import date, datetime

from web_app.models.pharmacie import PharmacieAttr, PharmacieUtils
from web_app.models.prescription import Prescription, PrescriptionUtils
from web_app.models.type_dict import Prescription_export_format


class PrescriptionUtilsUser:
    if TYPE_CHECKING:
        from web_app.connnected_user_web.connected_user import ConnectedUser

    connected_user: "ConnectedUser"
    user_id : int

    def __init__(self, connected_user: "ConnectedUser"):
        self.connected_user = connected_user
        self.user_id = connected_user.id

    def add_prescription(self, date: date, care_items: dict[str, int]) -> None:
        """Ajoute une nouvelle prescription et met à jour la pharmacie de l'utilisateur.

        Cette fonction enregistre une prescription à la date fournie pour les
        traitements indiqués, puis incrémente les entrées de pharmacie
        correspondantes pour l'année concernée.

        Arguments:
            * date (date): Date de la prescription à enregistrer
            * care_items (dict[str, int]): Dictionnaire des traitements
            prescrits et de leurs quantités
        """
        PrescriptionUtils.add_prescription(user_id=self.connected_user.id, date=date, care_items=care_items)
        PharmacieUtils.modify_pharmacie_year(user_id=self.user_id, year=date.year, attr= PharmacieAttr.total_enter, care_delta=care_items )
        
    def add_dlc_left(self, date: date, care_items: dict[str, int]) -> None:
        """Enregistre un retrait de traitements périmés et met à jour la pharmacie.

        Cette fonction vérifie que les quantités à retirer pour cause de DLC
        dépassée sont disponibles en stock, enregistre l'opération comme
        prescription de retrait, puis décrémente les stocks de la pharmacie
        pour l'année en cours.

        Arguments:
            * date (date): Date à laquelle les traitements sont retirés pour DLC dépassée
            * care_items (dict[str, int]): Dictionnaire des traitements retirés
            et de leurs quantités

        Lance:
            * ValueError: Si le stock restant serait négatif après le retrait
            des traitements indiqués
        """
        stock_delta = dict( - Counter(care_items))
        year = datetime.now().year
        if not PharmacieUtils.validat_quantity(user_id=self.user_id, year_to_verify=year, stock_delta=stock_delta) :
            raise ValueError("Stock insuffisant pour retirer le traitement")
            
        PrescriptionUtils.add_dlc_left(user_id=self.user_id, date=date, care_items=care_items)
        
        PharmacieUtils.modify_pharmacie_year(user_id=self.user_id,year=year, attr=PharmacieAttr.total_out_dlc, care_delta=care_items)

    def get_all_prescriptions(self) -> list[Prescription]:
        """Récupère toutes les prescriptions associées à l'utilisateur connecté.

        Cette fonction délègue à `PrescriptionUtils` la récupération de
        l'ensemble des prescriptions enregistrées en base de données pour
        l'identifiant utilisateur courant.

        Renvoie:
            * list[Prescription]: Liste de toutes les prescriptions de
            l'utilisateur connecté.
        """
        return PrescriptionUtils.get_all_prescriptions(user_id=self.user_id)

    def get_all_prescriptions_cares(self) -> list[Prescription_export_format]:
        """Récupère toutes les prescriptions au format d'export pour l'utilisateur connecté.

        Cette fonction délègue à `PrescriptionUtils` la récupération de
        l'ensemble des prescriptions de l'utilisateur, structurées dans un
        format prêt à être exporté ou traité par des outils externes.

        Renvoie:
            * list[Prescription_export_format]: Liste des prescriptions de
            l'utilisateur dans un format dédié à l'export.
        """
        return PrescriptionUtils.get_all_prescriptions_cares(user_id=self.user_id)

    def get_year_prescription(self, year: int) -> list[Prescription]:
        """Récupère toutes les prescriptions d'une année donnée pour l'utilisateur connecté.

        Cette fonction délègue à `PrescriptionUtils` la récupération des
        prescriptions dont la date appartient à l'année spécifiée et associées
        à l'identifiant utilisateur courant.

        Arguments:
            * year (int): Année pour laquelle récupérer les prescriptions

        Renvoie:
            * list[Prescription]: Liste des prescriptions enregistrées pour
            l'année demandée.
        """
        return PrescriptionUtils.get_year_prescription(user_id=self.user_id,year=year)

    def get_dlc_left_on_year(self ,year: int) -> list[Prescription]:
        """Récupère les retraits de traitements périmés pour une année donnée.

        Cette fonction délègue à `PrescriptionUtils` la récupération de toutes
        les prescriptions de type DLC dépassée enregistrées pour l'utilisateur
        courant sur l'année spécifiée.

        Arguments:
            * year (int): Année pour laquelle récupérer les retraits pour DLC dépassée

        Renvoie:
            * list[Prescription]: Liste des prescriptions correspondant aux
            retraits de traitements périmés sur l'année.
        """
        return PrescriptionUtils.get_dlc_left_on_year(user_id=self.user_id,year=year)

    
