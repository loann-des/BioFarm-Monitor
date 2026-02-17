from typing import TypedDict
from ..models import UserUtils

    
class Setting(TypedDict):
    """Stocke des réglages utilisateur, en l'occurrence les durées de
    tarissement et de préparation au vêlage.
    
    :var dry_time: int, Temps de tarissement (en jour)
    :var calving_preparation_time: int, Temps de préparation au vêlage (en jour)
    """

    dry_time: int  # Temps de tarrisement (en jour)
    calving_preparation_time: int  # Temps de prepa vellage (en jour)

class UserUtilsClient:
    id : int
    """Identifiant unique de l'utilisateur"""
    setting : Setting
    """Classe utilitaire pour gérer les interactions avec les utilisateurs"""
    email : str
    
    def __init__(self, user_id: int) -> None:
        self.id = user_id
        self.setting = self.get_user_setting(user_id)
        self.email = self.get_user_email(user_id)
        
    @staticmethod
    def set_user_setting(user_id : int, dry_time: int, calving_preparation: int) -> None:
        """Met à jour les réglages utilisateur concernant les durées de
        tarissement et de préparation du vêlage.

        Cette fonction envoi a l'API la mise à jour les durées de tarissement et de préparation
        du vêlage pour l'utilisateur associé à l'identifiant fourni en argument.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * dry_time (int): Durée de tarissement
            * calving_preparation (int): Durée de préparation au vêlage
        """

        UserUtils.set_user_setting( #TODO a remplaser par l'appel de l'api
            user_id=user_id, dry_time=dry_time, calving_preparation=calving_preparation
        )

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
        return Users.query.get(user_id) # type: ignore

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
        user : Users = Users.query.get(user_id) # type: ignore
        return user.medic_list # type: ignore
