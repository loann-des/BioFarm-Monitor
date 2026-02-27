import logging as lg

from typing import Any, TypedDict, TYPE_CHECKING

from ..models import Cow, CowUtils, UserUtils, Users, Traitement, Note, Reproduction

from datetime import date

import web_app.connected_user as ConnectedUser


class Traitement_signe(TypedDict):
    """
    Represente un traitement administré à une vache signé par son identifiant.

    :var cow_id: int, Identifiant de la vache
    :var traitement: Traitement, Traitement administré à la vache
    """
    cow_id: int  # date au format 'YYYY-MM-DD'
    traitement: Traitement



class Cow_Client:
    cow_id: int

    cow_cares: list[Traitement]
    """Liste de Traitement. Forme un dict {date_traitement: str,
    medicaments: dict[str, int], annotation: str)."""

    info: list[Note]
    """Notes générales. Forme une liste de tuples (date, contenu)."""

    in_farm: bool
    """True si la vache se trouve dans la ferme, False si elle en est sortie."""

    born_date: date | None
    """Date de naissance de la vache."""

    reproduction: list[Reproduction]
    """Liste des reproductions de la vache."""

    is_calf: bool
    """True si la vache est une génisse, False sinon."""

    init_as_cow: bool
    """True si la vache est comme vache adulte, False sinon."""
    
    def __init__(self,
                cow_id : int,
                cow_cares: list[Traitement] = [],
                info: list[Note] = [],
                in_farm: bool = True,
                born_date: date | None = None,
                reproduction: list[Reproduction] = [],
                is_calf: bool = False,
                init_as_cow: bool = True
                 ) -> None:
        self.cow_id = cow_id
        self.cow_cares = cow_cares
        self.info = info
        self.in_farm = in_farm
        self.born_date = born_date
        self.reproduction = reproduction
        self.is_calf = is_calf
        self.init_as_cow = init_as_cow


class CowUtilsClient:
    """Cette classe est un namespace. Tous ses membres sont statiques.

    Ce namespace regroupe les fonctions de gestion des vaches, de
    l'historique des traitements, et des données de reproduction.
    """
    cow_list: list[Cow_Client]
    """Cache local de l'ensemble des vaches d'un utilisateur pour limiter les accès à la base de données."""
    
    connected_user: "ConnectedUser.ConnectedUser"
    """connected_user est une référence à l'utilisateur connecté, utilisée pour accéder à son identifiant"""

    def __init__(self,
                 connected_user: ConnectedUser.ConnectedUser
                 ) -> None:
        cows: list[Cow] = CowUtils.get_all_cows(connected_user.id)
        self.cow_list = [
            Cow_Client(cow_id=cow.cow_id,
                       cow_cares = cow.cow_cares,
                       info = cow.info,
                       in_farm = cow.in_farm,
                       born_date = cow.born_date,
                       reproduction = cow.reproduction,
                       is_calf = cow.is_calf,
                       init_as_cow = cow.init_as_cow)
            for cow in cows

        ]

    # general cow functions ------------------------------------------------

    def get_cow(self, cow_id: int) -> Cow_Client | None:
        """Recherche une vache dans la base de données et renvoie un objet Cow
        si la vache a été trouvée.

        Arguments:
            * cow_id (int): Identifiant de la vache recherchée.

        Renvoie:
            * Cow: L'objet Cow correspondant à la vache associée à cow_id.

        Lance:
            * ValueError si la vache recherchée n'existe pas dans la base de
            données.
        """
        
        for cow in self.cow_list:
            if cow.cow_id == cow_id:
                return cow
        return None


    def get_all_cows(self) -> list[Cow_Client]:
        # TODO A été modifier
        """Renvoie l'ensemble des vaches d'un utilisateur.

        Cette fonction interroge la base de données et renvoie une liste de
        toutes les vaches associées à un utilisateur.

        Renvoie:
            * list[Cow]: Une liste contenant l'ensemble des vaches d'un
            utilisateur
        """
        return self.cow_list

    
    def add_cow(self, cow_id: int, born_date: date | None = None,
                init_as_cow: bool = True) -> None:
        """Ajoute une nouvelle vache à la base de données si elle n'existe pas
        déjà.

        Si aucune vache avec l'identifiant correspondant n'existe, alors elle
        est ajoutée à la base de données. Sinon une erreur est marquée dans le
        journal.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache à ajouter
            * born_date (date|None): Date de naissance
        """
        if self.get_cow(cow_id) is not None:
            lg.warning(f"(user :{self}, cow: {cow_id}) : already in database")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : already in database")

        new_cow = Cow_Client(
            cow_id=cow_id,
            born_date=born_date,
            init_as_cow=init_as_cow
        )
        if (
            CowUtils.add_cow(
                user_id=self.connected_user.id,
                cow_id=cow_id,
                born_date=born_date,
                init_as_cow=init_as_cow,
            ) ##TODO remplaser au passage a l'api
            or True #TODO retirer le or True pour activer la vérification du succès de l'ajout dans la base de données
        ):
            self.cow_list.append(new_cow)
            lg.info(f"(user :{self}, cow: {cow_id}) : upload in database")
        else:
            lg.warning(f"(user :{self}, cow: {cow_id}) : upload failed")

    
    def update_cow(self, cow_id: int, **kwargs: dict[str, Any]) -> None:
        """Met à jour les attributs d'une vache dans la base de données.

        Cette fonction recherche la vache associée à l'identifiant fourni, et
        met à jour ses attributs à partir des arguments nommés (kwargs).

        Arguments:
            * cow_id (int): Identifiant de la vache à modifier
            * **kwargs (dict[str, Any]): Les attributs à modifier (e.g. in_farm,
            born_date, etc.)
        """
        #TODO Gere les maintin de stock des medicament si modification de traitement
        cow: Cow_Client | None = self.get_cow(cow_id)
        
        if cow is None:
            lg.error(f"(user: {self}, cow: {cow_id}, fonction: update_cow): not in local list")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : doesn't exist in local list")
            

        
        if CowUtils.update_cow(
            user_id=self.connected_user.id,
            cow_id=cow_id,
            **kwargs
        )or True :#TODO remplaser au passage a l'api
            for key, value in kwargs.items():
                setattr(cow, key, value)
            lg.info(f"(user :{self}, cow: {cow_id}) : updated in database")
        
        else:
            lg.error(f"(user: {self}, cow: {cow_id}, fonction: update_cow): update_cow failed")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : update_cow failed")

    
    def suppress_cow(self, cow_id: int) -> None:
        """Retire une vache associée à un identifiant de la base de données.

        Cette fonction retire de la base de données la vache associée à
        l'identifiant fourni en argument et enregistre (commit) les changements.
        Si la vache n'existe pas, une erreur est marquée dans le journal.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
        """
        cow: Cow_Client | None = self.get_cow(cow_id)
        
        if cow is None:
            lg.error(f"(user: {self}, cow: {cow_id}, fonction: suppress_cow): not in local list")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : doesn't exist in local list")

        if CowUtils.suppress_cow(user_id=self.connected_user.id, cow_id=cow_id) or True: #TODO remplaser au passage a l'api
             self.cow_list.remove(cow)
             lg.info(f"(user :{self}, cow: {cow_id}) : delete in database")
             
        else:
            lg.error(f"(user: {self}, cow: {cow_id}, fonction: suppress_cow): delete failed")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : delete failed")

    
    def remove_cow(self, cow_id: int) -> None:
        """Enregistre la sortie d'une vache de la ferme en mettant à jour le
        statut de la vache.

        Si la vache associée à l'identifiant fourni existe, son statut est mis
        à jour et enregistré (commit) dans la base de données. Si la vache
        n'existe pas, une erreur est marquée dans le journal.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache à retirer de la ferme
        """
        cow: Cow | None
        if cow := Cow.query.get({"self": self, "cow_id": cow_id}):
            if not cow.in_farm:
                raise ValueError(
                    f"user :{self}, cow: {cow_id}: deja supprimé.")
            cow.in_farm = False
            db.session.commit()
            lg.info(f"(user :{self}, cow: {cow_id}): left the farm.")
        else:
            lg.warning(f"(user :{self}, cow: {cow_id}): not found.")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}): n'existe pas.")

    
    def add_calf(self, calf_id: int,
                 born_date: date | None = None) -> None:
        """Ajoute un veau à la base de données s'il n'existe pas déjà.

        S'il n'existe pas de veau associé à l'identifiant fourni, il est créé
        et ajouté à la base de données. Autrement, une erreur est marquée dans
        le journal et une ValueError est lancée.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * calf_id (int): Identifiant du veau
            * born_date (date): Date de naissance du veau

        Lance:
            * ValueError s'il existe déjà un veau associé à l'identifiant fourni
        """
        if not Cow.query.get({"self": self, "cow_id": calf_id}):
            new_cow = Cow(
                self=self,
                cow_id=calf_id,
                born_date=born_date,
                is_calf=True
            )
            db.session.add(new_cow)
            db.session.commit()
            lg.info(f"(user :{self}, cow: {calf_id}) : upload in database")
        else:
            lg.error(
                f"(user :{self}, cow: {calf_id}) : already in database")
            raise ValueError(
                f"(user :{self}, cow: {calf_id}) : already in database")

    # END general cow functions ------------------------------------------------

    # cow care functions ------------------------------------------------
    
    def add_cow_care(
        self, cow_id: int,  cow_care: Traitement
    ) -> tuple[int, date | None]:
        """Met à jour l'historique des traitements de la vache associée à
        l'identifiant fourni en argument.

        Si la vache existe, le traitement est ajouté et un tuple contenant le
        nombre de traitement restants et la date des prochains traitements est
        créé. Si la vache n'existe pas, une erreur est marquée dans le journal
        et la fonction renvoie None.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * cow_care (Traitement): Traitement à ajouter

        Retourne:
            * tuple ([int, date] | None): le nombre de traitements restants et
            la date du prochain, ou None si aucune vache associée à cow_id n'a
            été trouvée
        """
        # TODO Pas plus de traitements que de qt en stock
        # Récupérer la vache depuis la BDD
        cow: Cow | None
        if cow := Cow.query.get({"self": self, "cow_id": cow_id}):
            return CowUtils.add_care(cow, cow_care)
        lg.error(f"(user :{self}, cow: {cow_id})  not found.")
        raise ValueError(f"(user :{self}, cow: {cow_id})  n'existe pas.")

    
    def add_care(
        cow: Cow, cow_care: Traitement
    ) -> tuple[int, date | None]:
        """Ajoute un traitement à la vache spécifiée et renvoie les données de
        traitement mises à jour.

        Cette fonction ajoute une nouvelle entrée à la liste des traitements
        de la vache associée à l'identifiant fourni, enregistre (commit) les
        modifications, et calcule le nombre de traitements restants et la date
        du suivant.

        Arguments:
            * cow (Cow): L'objet Cow à mettre à jour
            * cow_cares (Tuplee[date, dict, str]): Les informations de
            traitement à ajouter

        Renvoie:
        * tuple[int, date]: Le nombre de traitements restants et la date du
        prochain
        """

        from .fonction import remaining_care_on_year, new_available_care
        # Ajouter le traitement à la liste
        cow.cow_cares.append(cow_care)

        # Commit les changements
        db.session.commit()

        lg.info(f"Care add to (user :{cow.self}, cow: {cow.cow_id}).")

        # traitement restant dans l'année glissante et date de nouveaux traitement diponible
        # type: ignore
        return remaining_care_on_year(cow=cow), new_available_care(cow=cow)

    
    def update_cow_care(
        self, cow_id: int, care_index: int, new_care: Traitement
    ) -> None:
        """Met à jour la liste de traitements d'une vache.

        Cette fonction met à jour la liste de traitements d'une vache au sein de
        la base de données. Lance une ValueError si aucune vache ne correspond
        à l'identifiant spécifié, et lance une IndexError si le traitement
        n'existe pas déjà dans la base de données.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache concernée
            * care_index (int): Position dans la liste du traitement à modifier
            * new_care (Traitement): Nouvelles données de traitement
        """
        cow: Cow | None
        if cow := Cow.query.get({"self": self, "cow_id": cow_id}):
            # Remplacement du soin dans la liste
            if care_index >= len(cow.cow_cares):
                raise IndexError("index out of bounds")
            cow.cow_cares[care_index] = new_care
            db.session.commit()

            lg.info(
                f"(user :{self}, cow: {cow_id}) : care updated in database")
        else:
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : doesn't exist in database")

    
    def delete_cow_care(self, cow_id: int, care_index: int) -> None:
        """Retire un traitement de la liste de traitements d'une vache

        Cette fonction retire le traitement à l'indice spécifié de la liste de
        traitements de la vache associée à l'identifiant fourni et enregistre
        (commit) le changement dans la base de données

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * care_index (int): Indice du traitement dans la liste
        """
        cow: Cow | None
        if cow := Cow.query.get({"self": self, "cow_id": cow_id}):
            del cow.cow_cares[care_index]
            db.session.commit()
            lg.info(
                f"(user :{self}, cow: {cow_id}) : care deleted in database")
        else:
            lg.error(f"(user :{self}, cow: {cow_id}) : not in database")
            raise ValueError(
                f"(user :{self}, cow: {cow_id}) : doesn't exist in database")

    
    def get_all_care(self) -> list[Traitement_signe]:
        """Retrieves all non-empty care records for all cows, sorted by date in
        descending order.

        This function collects all care records with non-empty treatment
        dictionaries from every cow and returns them as a list sorted by
        treatment date, most recent first.

        Returns:
            list[Traitement_signe]: A list of objects containing the cow ID and
            the associated treatment.
        """
        all_cares: list[Traitement_signe] = [
            Traitement_signe(cow_id=cow.cow_id, traitement=care)
            for cow in self.cow_list
            for care in cow.cow_cares
            if care  # filter out falsy / empty treatments
        ]
        # tri par date décroissante
        all_cares.sort(
            key=lambda t: t["traitement"]["date_traitement"],
            reverse=True,
        )
        return all_cares

    
    def get_care_by_id(self, cow_id: int,) -> list[Traitement] | None:
        """Renvoie la liste des traitements d'une vache

        Renvoie la liste des traitements de la vache associée à l'identifiant
        fourni si elle existe. Sinon, marque une erreur dans le journal et
        renvoie None.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Renvoie:
            * list[Traitement]: La liste des traitements de la vache
            spécifiéé si elle existe
        """
        cow: Cow_Client
        for cow in self.cow_list:
            if cow.cow_id == cow_id:
                return cow.cow_cares
        lg.error(f"(user :{self}, cow: {cow_id}) : not found.")
        raise ValueError(f"(user :{self}, cow: {cow_id}) : n'existe pas.")

    
    def get_care_on_year(self, year: int) -> list[Traitement]:
        """Récupère l'ensemble de l'historique de traitement des veaux sur une
        année spécifique.

        Cette fonction s'appuie sur le cache local `self.cow_list` pour
        collecter:
        - les traitements effectués sur les vaches marquées comme veaux, et
        - les traitements effectués avant la première insémination pour les
          vaches non initialisées comme adulte.
        """
        from web_app.fonction import parse_date

        res: list[Traitement] = [
            cow_care
            for cow in self.cow_list
            for cow_care in cow.cow_cares
            if (
                parse_date(cow_care["date_traitement"]).year == year
                and (
                    cow.is_calf
                    or (
                        not cow.init_as_cow
                        and cow.reproduction
                        and parse_date(cow_care["date_traitement"])
                        <= parse_date(cow.reproduction[0]["insemination"])
                    )
                )
            )
        ]
        return res

    
    def get_calf_care_on_year(self, year: int) -> list[Traitement]:
        """Récupère l'ensemble de l'historique de traitement des veaux sur une
        année spécifique.

        Cette fonction collecte l'ensemble des traitements effectués sur les
        vaches sans historique de reproduction et les traitements effectués  sur
        les vaches avant la date de leur première insémination, et les filtre
        pour correspondre à l'année fournie en argument.

        Arguments:
            * self (int): Identifiant de l'utilisateur.
            * year (int): Année au cours de laquelle ont eu lieu les
           traitements.

        Renvoie:
            * list[Traitement]: Une liste de traitements sur les veaux datant
            de l'année fournie en argument
        """
        from web_app.fonction import parse_date
        res: list[Traitement] = [
            cow_care
            # iteration sur cows
            for cow in Cow.query.filter_by(self=self).all()
            for cow_care in cow.cow_cares  # iteration sur cow_care
            if (
                parse_date(cow_care["date_traitement"]
                           ).year == year  # verif de l'année
                and (
                    cow.is_calf            # si c'est un veau
                    or (
                        not cow.init_as_cow  # sinon : non initialiser comme vache
                        and cow.reproduction   # et si il y'a eu reproduction
                        # et si traitement avant reproduction
                        and parse_date(cow_care["date_traitement"]) <= parse_date(cow.reproduction[0]["insemination"])
                    )
                )
            )
        ]
        return res

    # END cow care functions ------------------------------------------------

    # reproduction functions ------------------------------------------------

    
    def add_insemination(self, cow_id: int, insemination: str) -> None:
        # TODO Gestion doublon add_reproduction
        """Ajoute une entrée à l'historique d'insémination de la vache spécifiée

        Cette fonction ajoute une nouvelle insémination à l'historique de
        reproduction de la vache associée à l'identifiant fourni comme argument
        si elle existe. Sinon, marque une erreur dans le journal et lance une
        ValueError.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * insemination (str): Date d'insémination

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if cow := Cow.query.get({"self": self, "cow_id": cow_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            cow.reproduction.append(
                {
                    "insemination": insemination,
                    "ultrasound": None,
                    "dry":  None,
                    "dry_status":  False,  # status du tarrisement
                    "calving_preparation":  None,
                    "calving_preparation_status": False,  # status de prepa vellage
                    "calving_date":  None,
                    "calving":  False,  # status du vellage
                    "abortion": False,
                    "reproduction_details": None  # détails sur la reproduction
                }
            )
            cow.is_calf = False
            db.session.commit()
            lg.info(f"insemination on {insemination} add to {cow_id}")
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    
    def validated_ultrasound(self, cow_id: int, ultrasound: bool) -> None:
        """Valide ou invalide les résultats des ultrasons pour la dernière
        insémination d'une vache.

        Cette fonction met à jour les résultats des ultrasons dans l'historique
        de reproduction de la vache associée à l'identifiant fourni, ainsi que
        les dates de reproduction associées.Si la vache spécifiée n'existe pas,
        une ValueError est lancée.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * ultradound (bool): Résultats des ultrasons (True si confirmé,
            False si non confirmé)

        Lance:
            * ValueError si aucune vache dans la base n'est associée à
            l'identifiant fourni
        """
        from web_app.fonction import last
        cow: Cow | None
        if cow := Cow.query.get({"self": self, "cow_id": cow_id}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            reproduction: Reproduction | None = last(
                cow.reproduction)  # type: ignore
            if not reproduction:
                raise ValueError(f"cow : {cow_id} : n'as pas eté inseminé")
            reproduction["ultrasound"] = ultrasound

            if ultrasound:

                cow.reproduction[-1] = CowUtils.set_reproduction(
                    self, reproduction)
                lg.info(f"insemination on {date} of {cow_id} confirm")
            else:
                lg.info(f"insemination on {date} of {cow_id} invalidate")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    
    # TODO fonction Pure calculatoir peut etre sortir pour fonction.py ?
    def set_reproduction(self, reproduction: Reproduction) -> Reproduction:
        """Calcule les dates de reproduction pour une vache en fonction de sa
        date d'insémination et des réglages utilisateur.

        Cette fonction met à jour le dictionnaire de reproduction avec les
        durées de tarissage, de préparation et la date de vêlage calculés.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * reproduction (Reproduction): Les données de reproduction à mettre
            à jour

        Renvoie:
            * Reproduction: Les données de reproduction mises à jour, avec les
            dates calculées
        """
        from web_app.fonction import substract_date_to_str, sum_date_to_str
        user: Users = UserUtils.get_user(self=self)
        calving_date: str = sum_date_to_str(reproduction["insemination"], 280)
        print("calving_date ok")
        reproduction["dry"] = substract_date_to_str(
            calving_date, int(user.setting["dry_time"]))  # type: ignore
        print("dry ok")
        reproduction["calving_preparation"] = substract_date_to_str(
            # type: ignore
            calving_date, int(user.setting["calving_preparation_time"]))
        reproduction["calving_date"] = calving_date
        return reproduction

    
    def get_reproduction(self, cow_id: int) -> Reproduction:
        """Récupère la dernière reproduction de la vache spécifiée.

        Renvoie l'entrée de reproduction la plus récente de la vache associée
        à l'identifiant fourni, ou lance une ValueError si la vache n'existe
        pas, n'est plus dans la ferme ou n'a aucune reproduction.
        """
        # récupère la vache depuis le cache client
        cow = self.get_cow(cow_id)

        if not cow.in_farm:
            raise ValueError(f"cow : {cow_id} : est supprimer")

        if not cow.reproduction:
            raise ValueError(f"cow : {cow_id} : n'a pas de reproduction")

        return cow.reproduction[-1]
    
    def reload_all_reproduction(self) -> None:
        """Recalcule les dates associées à la dernière reproduction des vaches.

        Cette fonction parcourt la liste des vaches et recalcule pour chacune
        les dates clefs liées à la reproduction la plus récente dans son
        historique et enregistre (commit) les changements dans la base de
        données.

        Arguments:
            * self (int): Identifiant de l'utilisateur
        """
        from .fonction import last

        cows: list[Cow] = Cow.query.filter_by(self=self, in_farm=True).all()
        for cow in cows:
            if (last(cow.reproduction)
                and cow.reproduction[-1].get("ultrasound")
                    and not cow.reproduction[-1].get("calving")):

                cow.reproduction[-1] = CowUtils.set_reproduction(
                    self,
                    cow.reproduction[-1])

        db.session.commit()
        lg.info("reproduction reload")

    
    def get_valid_reproduction(self) -> dict[int, Reproduction]:
        """Récupère la dernière entrée de reproduction valide pour toutes les
        vaches dont les ultrasons ont été confirmés.

        Cette fonction s'appuie sur le cache local `self.cow_list` et renvoie un
        dictionnaire associant l'identifiant de chaque vache à leur reproduction
        la plus récente où:
        - les ultrasons sont confirmés, et
        - le vêlage n'a pas encore été effectué.
        """
        from web_app.fonction import last

        return {
            cow.cow_id: cow.reproduction[-1]
            for cow in self.cow_list
            if cow.in_farm
            and last(cow.reproduction)
            and cow.reproduction[-1].get("ultrasound")
            and not cow.reproduction[-1].get("calving")
        }

    
    def validated_calving(cow_id: int, self, abortion: bool,
                          info: str | None = None) -> None:
        """Valide le vêlage pour une vache et enregistre si c'était un
        avortement.

        Cette fonction met à jour la dernière reproduction de la vache spécifiée
        pour indiquer un vêlage, et enregistrer si c'était un avortement ou non.
        Si aucune vache n'est associée à l'identifiant fourni en argument, une
        erreur est marquée dans le journal et une ValueError est lancée.

        Arguments:
            * cow_id (int): Identifiant de la vache
            * self (int): Identifiant de l'utilisateur
            * abortion (bool): True si le vêlage était un avortement, False
            sinon
            * info (str | None): Notes et commentaires

        Lance:
            * ValueError si la vache n'existe pas
        """
        # TODO gestion pas d'insemination reproduction_ultrasound calving
        # TODO getstion de l'anotation
        cow: Cow | None
        if cow := Cow.query.get({'cow_id': cow_id, 'self': self}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")

            reproduction: Reproduction = cow.reproduction[-1]
            reproduction["calving"] = True
            reproduction["abortion"] = abortion
            cow.reproduction[-1] = reproduction

            lg.info(f"calving of of {cow_id} confirm")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    
    def validated_dry(self, cow_id: int) -> None:
        """Valide le tarissage d'une vache.

        Cette fonction met à jour l'historique de reproduction pour la vache
        associée à l'identifiant fourni en argument pour indiquer que la période
        de tarissage est terminée. Si la vache n'existe pas, une erreur est
        marquée dans le journal et une ValueError est lancée.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Lance:
            * ValueError si aucune vache ne correspond à l'identifiant fourni
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id': cow_id, 'self': self}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")

            try:
                reproduction: Reproduction = cow.reproduction[-1]
                reproduction["dry_status"] = True
                cow.reproduction[-1] = reproduction

                lg.info(f"dry of of {cow_id} confirm")

                db.session.commit()
            except Exception as e:
                lg.error(f"Error updating dry status for cow {cow_id}: {e}")
                raise
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    
    def validated_calving_preparation(self, cow_id: int) -> None:
        """Valide la date de préparation du vêlage pour une vache.

        Cette fonction met à jour la dernière entrée de l'historique de
        reproduction de la vache associée à l'identifiant fourni en argument
        pour indiquer que la préparation au vêlage a bien été effectuée. Si la
        vache spécifiée n'existe pas, une erreur est marquée dans le journal et
        une ValueError est lancée.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id': cow_id, 'self': self}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            reproduction: Reproduction = cow.reproduction[-1]
            reproduction["calving_preparation_status"] = True
            cow.reproduction[-1] = reproduction

            lg.info(f"calving preparation of of {cow_id} confirm")

            db.session.commit()
        else:
            lg.error(f"Cow with {cow_id} not found.")
            raise ValueError(f"{cow_id} n'existe pas.")

    
    def update_cow_reproduction(
        self,
        cow_id: int,
        repro_index: int,
        new_repro: Reproduction,
    ) -> None:
        """Met à jour une entrée de reproduction d'une vache.

        Cette fonction remplace l'entrée de reproduction à l'indice fourni en
        argument par un nouveau dictionnaire de reproduction, et enregistre
        (commit) le changement dans la base de données.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * repro_index (int): Indice de l'entrée dans l'historique
            * new_repro (Reproduction): Entrée de reproduction à insérer dans
            l'historique
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id': cow_id, 'self': self}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            cow.reproduction[repro_index] = new_repro
            db.session.commit()
            lg.info(f"{cow_id} : reproduction updated in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    
    def delete_cow_reproduction(self, cow_id: int, repro_index: int) -> None:
        """Supprime une entrée de l'historique de reproduction d'une vache.

        Cette fonction supprime l'entrée présente à l'indice fourni de
        l'historique de reproduction de la vache et enregistre (commit) les
        changements dans la base de données. Si la vache spécifiée n'existe pas,
        une erreur est marquée dans le journal et une ValueError est lancée.

        Arguments:
            * self (int): Identifiant de l'utilisateur
            * cow_id (int): Identifiant de la vache
            * repro_index (int): Indice dans l'historique de l'entrée à
            supprimer

        Lance:
            * ValueError si la vache spécifiée n'existe pas
        """
        cow: Cow | None
        if cow := Cow.query.get({'cow_id': cow_id, 'self': self}):
            if not cow.in_farm:
                raise ValueError(f"cow : {cow_id} : est supprimer")
            del cow.reproduction[repro_index]
            db.session.commit()
            lg.info(f"{cow_id} : reproduction deleted in database")
        else:
            lg.error(f"{cow_id} : not in database")
            raise ValueError(f"{cow_id} : doesn't exist in database")

    # END reproduction functions ------------------------------------------------
