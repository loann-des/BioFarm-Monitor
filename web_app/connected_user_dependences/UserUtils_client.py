from typing import TypedDict, TYPE_CHECKING

from ..models import UserUtils, Users
    
import web_app.connected_user as Connected_user
class Setting(TypedDict):
    """Stocke des réglages utilisateur, en l'occurrence les durées de
    tarissement et de préparation au vêlage.
    
    :var dry_time: int, Temps de tarissement (en jour)
    :var calving_preparation_time: int, Temps de préparation au vêlage (en jour)
    """

    dry_time: int  # Temps de tarrisement (en jour)
    calving_preparation_time: int  # Temps de prepa vellage (en jour)

class UserUtilsClient:
    
    # if TYPE_CHECKING:
    #     from ..connected_user import ConnectedUser
        
    id : int
    """Identifiant unique de l'utilisateur"""
    setting : Setting
    """Classe utilitaire pour gérer les interactions avec les utilisateurs"""
    email : str
    """TODO doc"""
    medic_list : dict[str, str]
    """Un dictionaitre de medicament : type de mesure ( ex : doliprane : ml)"""
    connected_user= None # : Connected_user.ConnectedUser
    """L'utilisateur connecté associé à ce client utils"""
    
    def __init__(self, user_id: int, connected_user) -> None:
        from web_app.connected_user import ConnectedUser

        """Initialise un client d'utilisateurs avec les informations de base.
        
        Ce constructeur charge les réglages et l'adresse e-mail associés à l'identifiant utilisateur fourni.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur dont il faut charger les informations
        """
        self.id = user_id
        user: Users = UserUtils.get_user(user_id) #TODO requtet api
        self.setting = user.setting
        self.email = user.email
        self.medic_list = user.medic_list
        self.connected_user = connected_user
        self.connected_user.id= self.id

        
    def set_connected_user(self, connected_user):
        from web_app.connected_user import ConnectedUser

        self.connected_user = connected_user
        self.connected_user.id= self.id
        
    def set_user_setting(self, dry_time: int, calving_preparation: int) -> None:
        """Met à jour les réglages de l'utilisateur pour les durées de tarissement et de préparation au vêlage.

        Cette fonction enregistre les nouvelles valeurs des réglages côté persistance puis met à jour l'état local du client.

        Arguments:
            * dry_time (int): Nouvelle durée de tarissement (en jours)
            * calving_preparation (int): Nouvelle durée de préparation au vêlage (en jours)
        """
        UserUtils.set_user_setting( #TODO a remplaser par l'appel de l'api
            user_id=self.id , dry_time=dry_time, calving_preparation=calving_preparation
        )
        #if(statut == true) # si retour a vrais aplliquer modif en local
        self.setting["dry_time"] = dry_time
        self.setting["calving_preparation_time"] = calving_preparation

    def get_user_setting(self) -> Setting:
        """Récupère les réglages utilisateur de durée de tarissement et de
        préparation au vêlage

        Cette fonction retourne le dictionnaire des réglages de l'utilisateur
        associé à l'identidiant fourni en argument concernant les durées de
        tarissement et de préparation au vêlage.

        Renvoie:
            * Settings: les réglages utilisateur de durée de tarissement et de
            préparation au vêlage
        """
        return self.setting

    def add_medic_in_pharma_list(self, medic: str, mesur: str) -> None:
        """Ajoute un médicament à la pharmacie.

        Cette fonction ajoute un médicament à la pharmacie de l'utilisateur s'il
        n'existe pas déjà. S'il existe déjà, une erreur est marquée dans le
        journal.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur
            * medic (str): Nom du médicament
            * mesur (int): Quantité de médicament
        """
        UserUtils.add_medic_in_pharma_list(self.id, medic=medic, mesur=mesur) #TODO a remplaser par l'appel de l'api
        #if(statut == true) # si retour a vrais aplliquer modif en local
        self.medic_list.setdefault(medic,mesur)

    def get_pharma_list(self) -> dict[str, str]:
        """Récupère la liste des médicaments dans la pharmacie de l'utilisateur.

        Cette fonction renvoie un dictionnaire contenant les médicaments
        présents dans la pharmacie de l'utilisateur ainsi que leurs quantité.

        Arguments:
            * user_id (int): Identifiant de l'utilisateur

        Renvoie:
            * dict[str, int]: Un dictionnaire associant les noms des médicaments
            à leurs quantités
        """
        return self.medic_list
