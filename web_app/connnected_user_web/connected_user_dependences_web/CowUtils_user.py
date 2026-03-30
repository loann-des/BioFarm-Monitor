from collections import Counter
import logging as lg

from typing import TYPE_CHECKING, Any


from datetime import date

from web_app.fonction import parse_date
from web_app.models.cow import Cow, CowUtils
from web_app.models.pharmacie import PharmacieAttr, PharmacieUtils
from web_app.models.type_dict import Note, Reproduction, Traitement, Traitement_signe


class CowUtilsUser:

    if TYPE_CHECKING:
        from web_app.connnected_user_web.connected_user import ConnectedUser

    user: "ConnectedUser"
    """connected_user est une référence à l'utilisateur connecté"""

    user_id: int
    """identifiant de l'utilisateur connecté'"""


    def __init__(self, user: "ConnectedUser") -> None:
        self.user_id = user.id
        self.user = user

    # general cow functions ------------------------------------------------

    def get_cow(self, cow_id: int) -> Cow | None:
        """Récupère une vache associée à l'utilisateur courant à partir de son identifiant.

        Cette fonction interroge la couche utilitaire `CowUtils` pour obtenir
        l'objet `Cow` correspondant à l'identifiant fourni et lié à l'utilisateur.

        Arguments:
            * cow_id (int): Identifiant de la vache à récupérer

        Renvoie:
            * Cow | None: L'objet `Cow` correspondant si trouvé, sinon None
        """
        CowUtils.get_care_by_id(user_id=self.user_id, cow_id=cow_id)

    def get_all_cows(self) -> list[Cow]:
        """Récupère l'ensemble des vaches associées à l'utilisateur courant.

        Cette fonction interroge la couche utilitaire `CowUtils` pour retourner
        la liste complète des vaches liées à l'identifiant de l'utilisateur.

        Arguments:
            * self (int): Identifiant de l'utilisateur

        Renvoie:
            * list[Cow]: La liste des vaches associées à l'utilisateur
        """
        return CowUtils.get_all_cows(user_id=self.user_id)

    def add_cow(self, cow_id: int, cow_name: str | None = None, born_date: date | None = None,
                init_as_cow: bool = True) -> None:
        """Ajoute une nouvelle vache pour l'utilisateur courant dans la base de données.

        Cette fonction crée une vache avec l'identifiant fourni, lui associe
        éventuellement un nom et une date de naissance, puis délègue son
        enregistrement à la couche utilitaire `CowUtils`.

        Arguments:
            * cow_id (int): Identifiant de la vache à ajouter
            * cow_name (str | None): Nom de la vache à enregistrer si fourni
            * born_date (date | None): Date de naissance de la vache si connue
            * init_as_cow (bool): Indique si l'animal doit être initialisé
            directement comme vache adulte
        """
        CowUtils.add_cow(
            user_id=self.user_id,
            cow_id=cow_id,
            born_date=born_date,
            init_as_cow=init_as_cow,
        )
        if cow_name:
            CowUtils.set_cow_name(user_id=self.user_id,
                                  cow_id=cow_id, cow_name=cow_name)

    def update_cow(self, cow_id: int, **kwargs: dict[str, Any]) -> None:
        """Met à jour les informations d'une vache associée à l'utilisateur courant.

        Cette fonction délègue à `CowUtils` la mise à jour des champs fournis
        pour la vache identifiée, tout en empêchant la modification directe des
        traitements pour préserver la cohérence du stock de médicaments.

        Arguments:
            * cow_id (int): Identifiant de la vache à mettre à jour
            * kwargs (dict[str, Any]): Champs et valeurs à mettre à jour pour la vache

        Lance:
            * NotImplementedError: Si une tentative de modification de `cow_cares`
            est détectée dans les paramètres.
        """
        if "cow_cares" in kwargs:
            raise NotImplementedError(
                "La modification de cow_cares doit être gérée via les fonctions d'ajout, de suppression et de modification de traitement dédiées pour assurer la cohérence du stock de médicaments.")

        CowUtils.update_cow(
            user_id=self.user_id,
            cow_id=cow_id,
            **kwargs)

    def suppress_cow(self, cow_id: int) -> None:
        """Supprime définitivement une vache associée à l'utilisateur courant.

        Cette fonction délègue à `CowUtils` la suppression de la vache
        identifiée pour l'utilisateur, ce qui retire définitivement ses données
        de la base.

        Arguments:
            * cow_id (int): Identifiant de la vache à supprimer définitivement
        """
        CowUtils.suppress_cow(user_id=self.user_id, cow_id=cow_id)

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
        CowUtils.remove_cow(user_id=self.user_id, cow_id=cow_id)

    def add_calf(self, calf_id: int,
                 born_date: date | None = None,
                 calf_name: str | None = None) -> None:
        """Ajoute un nouveau veau pour l'utilisateur courant dans la base de données.

        Cette fonction enregistre un animal comme veau avec l'identifiant
        fourni, lui associe éventuellement un nom et une date de naissance, puis
        délègue son enregistrement à la couche utilitaire `CowUtils`.

        Arguments:
            * calf_id (int): Identifiant du veau à ajouter
            * born_date (date | None): Date de naissance du veau si connue
            * calf_name (str | None): Nom du veau à enregistrer si fourni
        """
        CowUtils.add_cow(
            user_id=self.user_id,
            cow_id=calf_id,
            born_date=born_date,
        )
        if calf_name:
            CowUtils.set_cow_name(user_id=self.user_id,
                                  cow_id=calf_id, cow_name=calf_name)

    # END general cow functions ------------------------------------------------

    # cow care functions ------------------------------------------------

    def add_cow_care(
        self, cow_id: int,  cow_care: Traitement
    ) -> tuple[int, date | None]:
        """Ajoute un traitement à une vache et met à jour les stocks de médicaments.

        Cette fonction vérifie la disponibilité des médicaments nécessaires,
        met à jour les stocks en pharmacie si le traitement est valide, puis
        enregistre le traitement pour la vache spécifiée.

        Arguments:
            * cow_id (int): Identifiant de la vache à traiter
            * cow_care (Traitement): Données du traitement à appliquer à la vache

        Renvoie:
            * tuple[int, date | None]: Informations retournées par `CowUtils.add_cow_care`,
            le nombre de traitements restants et la date de disponibilité d'un nouveau traitement.
        """
        year: int = parse_date(cow_care["date_traitement"]).year

        stock_delta = dict(- Counter(cow_care["medicaments"]))
        # verifi le validité des stock apres traitement
        if PharmacieUtils.validat_quantity(user_id=self.user_id,
                                           stock_delta=stock_delta,
                                           year_to_verify=year):
            # MAJ les stock
            PharmacieUtils.modify_pharmacie_year(user_id=self.user_id,
                                                 year=year,
                                                 attr=PharmacieAttr.total_used,
                                                 care_delta=cow_care["medicaments"])
        # ajout du traitement
        return CowUtils.add_cow_care(user_id=self.user_id, cow_id=cow_id, cow_care=cow_care)

    def update_cow_care(
        self, cow_id: int, care_index: int, new_care: Traitement
    ) -> None:
        """Met à jour un traitement existant d'une vache et ajuste les stocks de médicaments.

        Cette fonction calcule la différence entre l'ancien et le nouveau
        traitement, vérifie la disponibilité en pharmacie, met à jour les
        stocks correspondants, puis enregistre la modification du traitement.

        Arguments:
            * cow_id (int): Identifiant de la vache dont le traitement doit être mis à jour
            * care_index (int): Indice du traitement dans la liste des soins de la vache
            * new_care (Traitement): Nouveau traitement à appliquer à la vache

        Lance:
            * ValueError: Si la mise à jour du traitement conduirait à un stock de médicaments négatif
        """
        if cow := self.get_cow(cow_id=cow_id):
            old_care = cow.cow_cares[care_index]["medicaments"]
            year = parse_date(new_care["date_traitement"]).year
            care_delta = dict(Counter(new_care) - Counter(old_care))
            stock_delta = dict(- Counter(care_delta))
            if PharmacieUtils.validat_quantity(user_id=self.user_id, stock_delta=stock_delta, year_to_verify=year):
                if cow.is_calf_care(new_care):
                    PharmacieUtils.modify_pharmacie_year(
                        user_id=self.user_id, year=year, attr=PharmacieAttr.total_used_calf, care_delta=care_delta)
                else:
                    PharmacieUtils.modify_pharmacie_year(
                        user_id=self.user_id, year=year, attr=PharmacieAttr.total_used, care_delta=care_delta)
                CowUtils.update_cow_care(
                    user_id=self.user_id, cow_id=cow_id, care_index=care_index, new_care=new_care)
            else:
                raise ValueError("Stock en negatif apres opperation")

    def delete_cow_care(self, cow_id: int, care_index: int) -> None:
        """Supprime un traitement d'une vache et ajuste les stocks de médicaments.

        Cette fonction retire un soin de l'historique de la vache, met à jour
        les stocks de médicaments en pharmacie en conséquence, puis enregistre
        la suppression du traitement.

        Arguments:
            * cow_id (int): Identifiant de la vache dont le traitement doit être supprimé
            * care_index (int): Indice du traitement dans la liste des soins de la vache
        """
        if cow := self.get_cow(cow_id=cow_id):
            care = cow.cow_cares[care_index]
            year = parse_date(care["date_traitement"]).year
            stock_delta = care["medicaments"]
            care_delta = dict(- Counter(care["medicaments"]))
            if cow.is_calf_care(traitement=care):
                PharmacieUtils.modify_pharmacie_year(
                    user_id=self.user_id, year=year, attr=PharmacieAttr.total_used_calf, care_delta=care_delta)
            else:
                PharmacieUtils.modify_pharmacie_year(
                    user_id=self.user_id, year=year, attr=PharmacieAttr.total_used, care_delta=care_delta)

            CowUtils.delete_cow_care(
                user_id=self.user_id, cow_id=cow_id, care_index=care_index)

    def get_all_care(self) -> list[Traitement_signe]:
        """Récupère l'ensemble des traitements signés pour l'utilisateur courant.

        Cette fonction délègue à `CowUtils` la récupération de tous les
        traitements administrés aux vaches, en les associant à l'identifiant de
        chaque vache concernée.

        Renvoie:
            * list[Traitement_signe]: Liste des traitements signés par
            identifiant de vache
        """
        return CowUtils.get_all_care(user_id=self.user_id)

    def get_care_by_id(self, cow_id: int,) -> list[Traitement] | None:
        """Récupère l'historique des traitements d'une vache pour l'utilisateur courant.

        Cette fonction délègue à `CowUtils` la récupération de la liste des
        traitements associés à une vache identifiée pour l'utilisateur, ou None
        si aucun traitement n'est trouvé.

        Arguments:
            * cow_id (int): Identifiant de la vache dont on souhaite obtenir
            les traitements

        Renvoie:
            * list[Traitement] | None: Liste des traitements de la vache ou
            None si aucun traitement n'est enregistré
        """
        return CowUtils.get_care_by_id(user_id=self.user_id, cow_id=cow_id)

    def get_care_on_year(self, year: int) -> list[Traitement]:
        """Récupère l'ensemble des traitements effectués sur une année donnée pour l'utilisateur courant.

        Cette fonction délègue à `CowUtils` la récupération de tous les
        traitements enregistrés dont la date correspond à l'année fournie en
        argument pour l'utilisateur.

        Arguments:
            * year (int): Année pour laquelle récupérer les traitements

        Renvoie:
            * list[Traitement]: Liste des traitements correspondant à l'année
            spécifiée
        """
        return CowUtils.get_care_on_year(user_id=self.user_id, year=year)

    def get_calf_care_on_year(self, year: int) -> list[Traitement]:
        """Récupère tous les traitements réalisés sur les veaux pour une année donnée.

        Cette fonction délègue à `CowUtils` la récupération de l'ensemble des
        soins administrés aux veaux dont la date de traitement correspond à
        l'année spécifiée pour l'utilisateur courant.

        Arguments:
            * year (int): Année pour laquelle récupérer les traitements des veaux

        Renvoie:
            * list[Traitement]: Liste des traitements des veaux pour l'année
            spécifiée
        """
        return CowUtils.get_calf_care_on_year(user_id=self.user_id, year=year)

    # END cow care functions ------------------------------------------------

    # reproduction functions ------------------------------------------------

    def add_insemination(self, cow_id: int, insemination: str) -> None:
        """Ajoute une nouvelle insémination pour une vache de l'utilisateur courant.

        Cette fonction enregistre une date d'insémination pour la vache
        identifiée et délègue la création de l'entrée de reproduction à
        `CowUtils`.

        Arguments:
            * cow_id (int): Identifiant de la vache à inséminer
            * insemination (str): Date d'insémination au format chaîne
        """
        # TODO Gestion doublon add_reproduction
        CowUtils.add_insemination(
            user_id=self.user_id, cow_id=cow_id, insemination=insemination)

    def validated_ultrasound(self, cow_id: int, ultrasound: bool) -> None:
        """Valide ou invalide le résultat de l'échographie pour une vache.

        Cette fonction délègue à `CowUtils` la mise à jour de l'état
        d'échographie d'une vache et transmet les paramètres de durée de
        tarissement et de préparation au vêlage issus des réglages de
        l'utilisateur.

        Arguments:
            * cow_id (int): Identifiant de la vache concernée par l'échographie
            * ultrasound (bool): Indique si l'échographie est confirmée (True)
            ou non (False)
        """
        CowUtils.validated_ultrasound(user_id=self.user_id, cow_id=cow_id, ultrasound=ultrasound,
                                      dry_time=self.user.setting["dry_time"], calving_preparation_time=self.user.setting["calving_preparation_time"])

    def get_reproduction(self, cow_id: int) -> Reproduction:
        """Récupère les informations de reproduction d'une vache pour l'utilisateur courant.

        Cette fonction délègue à `CowUtils` la récupération de la structure de
        données de reproduction associée à la vache identifiée et liée à
        l'utilisateur.

        Arguments:
            * cow_id (int): Identifiant de la vache dont on souhaite obtenir
            les informations de reproduction

        Renvoie:
            * Reproduction: Données de reproduction associées à la vache
        """
        return CowUtils.get_reproduction(user_id=self.user_id, cow_id=cow_id)

    def reload_all_reproduction(self) -> None:
        """Recharge l'ensemble des informations de reproduction pour toutes les vaches de l'utilisateur.

        Cette fonction délègue à `CowUtils` la régénération des données de
        reproduction en utilisant les paramètres de durée de tarissement et de
        préparation au vêlage définis dans les réglages de l'utilisateur.

        Renvoie:
            * None
        """
        CowUtils.reload_all_reproduction(
            user_id=self.user_id, dry_time=self.user.setting["dry_time"], calving_preparation_time=self.user.setting["calving_preparation_time"])

    def get_valid_reproduction(self) -> dict[int, Reproduction]:
        """Récupère les reproductions validées pour toutes les vaches de l'utilisateur.

        Cette fonction délègue à `CowUtils` la récupération des reproductions
        considérées comme valides, et les retourne sous forme de dictionnaire
        indexé par identifiant de vache.

        Renvoie:
            * dict[int, Reproduction]: Dictionnaire des reproductions valides
            indexé par identifiant de vache
        """
        return CowUtils.get_valid_reproduction(user_id=self.user_id)

    def validated_calving(self, cow_id: int, abortion: bool,
                          info: str | None = None) -> None:
        """Valide un vêlage ou un avortement pour une vache de l'utilisateur courant.

        Cette fonction délègue à `CowUtils` l'enregistrement de l'événement de
        reproduction correspondant, en indiquant s'il s'agit d'un vêlage mené à
        terme ou d'un avortement, et en ajoutant éventuellement une
        information complémentaire.

        Arguments:
            * cow_id (int): Identifiant de la vache concernée par l'événement
            * abortion (bool): Indique s'il s'agit d'un avortement (True) ou
            d'un vêlage normal (False)
            * info (str | None): Informations complémentaires à propos de
            l'événement si nécessaire
        """
        CowUtils.validated_calving(
            user_id=self.user_id, cow_id=cow_id, abortion=abortion, info=info)

    def validated_dry(self, cow_id: int) -> None:
        """Valide la mise à tarir d'une vache pour l'utilisateur courant.

        Cette fonction délègue à `CowUtils` l'enregistrement de l'état de tarissement
        pour la vache identifiée, afin de mettre à jour son suivi de reproduction
        et de production laitière.

        Arguments:
            * cow_id (int): Identifiant de la vache à mettre en tarissement
        """
        CowUtils.validated_dry(user_id=self.user_id, cow_id=cow_id)

    def validated_calving_preparation(self, cow_id: int) -> None:
        """Valide la préparation au vêlage d'une vache pour l'utilisateur courant.

        Cette fonction informe `CowUtils` que la vache identifiée entre en
        phase de préparation au vêlage, afin de mettre à jour son suivi de
        reproduction en conséquence.

        Arguments:
            * cow_id (int): Identifiant de la vache en préparation de vêlage
        """
        CowUtils.validated_calving_preparation(
            user_id=self.user_id, cow_id=cow_id)

    def update_cow_reproduction(
        self,
        cow_id: int,
        repro_index: int,
        new_repro: Reproduction,
    ) -> None:
        """Met à jour une entrée de l'historique de reproduction d'une vache.

        Cette fonction délègue à `CowUtils` la modification d'un événement de
        reproduction spécifique identifié par son indice dans l'historique de
        la vache pour l'utilisateur courant.

        Arguments:
            * cow_id (int): Identifiant de la vache dont on met à jour l'historique
            * repro_index (int): Indice de l'entrée de reproduction à modifier
            * new_repro (Reproduction): Nouvelles données de reproduction à enregistrer
        """
        CowUtils.update_cow_reproduction(
            user_id=self.user_id, cow_id=cow_id, repro_index=repro_index, new_repro=new_repro)

    def delete_cow_reproduction(self, cow_id: int, repro_index: int) -> None:
        """Supprime une entrée de l'historique de reproduction d'une vache.

        Cette fonction délègue à `CowUtils` la suppression d'un événement de
        reproduction identifié par son indice dans l'historique de la vache
        pour l'utilisateur courant.

        Arguments:
            * cow_id (int): Identifiant de la vache dont on supprime l'événement
            * repro_index (int): Indice de l'entrée de reproduction à supprimer
        """
        CowUtils.delete_cow_reproduction(user_id=self.user_id, cow_id=cow_id, repro_index=repro_index)

    # END reproduction functions ------------------------------------------------
