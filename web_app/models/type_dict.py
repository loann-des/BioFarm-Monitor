from typing import TypedDict

class Traitement(TypedDict):
    """
    Represente un traitement administré à une vache.

    :var date_traitement: str, Date du traitement au format 'YYYY-MM-DD'
    :var medicaments: dict[str, int], Dictionnaire des médicaments et dosages administrés
    :var annotation: str, Annotation ou remarque sur le traitement
    """
    date_traitement: str  # date au format 'YYYY-MM-DD'
    medicaments: dict[str, int]  # [medicament,dosage]
    annotation: str


class Traitement_signe(TypedDict):
    """
    Represente un traitement administré à une vache signé par son identifiant.

    :var cow_id: int, Identifiant de la vache
    :var traitement: Traitement, Traitement administré à la vache
    """
    cow_id: int  # date au format 'YYYY-MM-DD'
    traitement: Traitement


class Note(TypedDict):
    """
    Represente une note generale sur une vache.

    :var date_note: str, Date au format 'YYYY-MM-DD'
    :var information: str, information de la note
    """
    Redate_note: str
    """date au format 'YYYY-MM-DD"""
    information: str
    """information de la note"""


class Reproduction(TypedDict):
    """Représente le statut reproductif d'une  vache.

    :var insemination: str, Date d'insémination au format 'YYYY-MM-DD'
    :var ultrasound: bool | None, Résultats de l'échographie. True si la vache porte un veau, False sinon
    :var dry: str | None, Date de tarissement au format 'YYYY-MM-DD'
    :var dry_status: bool, Tarissement d'une vache. True si la vache est tarie, False sinon
    :var calving_preparation: str | None, Date de préparation au vêlage au format 'YYYY-MM-DD'
    :var calving_preparation_status: bool, Statut de préparation au vêlage. True si la vache est en préparation au vêlage, False sinon
    :var calving_date: str | None, Date de vêlage au format 'YYYY-MM-DD'
    :var calving: bool, Statut du vêlage. True si la vache a vêlé, False sinon
    :var abortion: bool, Avortement. True si un avortement a eu lieu, False sinon
    :var reproduction_details: str | None, Détails sur la reproduction
    """

    insemination: str
    """Date d'insémination au format 'YYYY-MM-DD'."""

    ultrasound: bool | None
    """Résultats de l'échographie. True si la vache porte un veau, False
    sinon."""

    dry: str | None
    """Date de tarissement au format 'YYYY-MM-DD'."""

    dry_status: bool  # status du tarrisement
    """Tarissement d'une vache. True si la vache est en tarissement, False
    sinon."""

    calving_preparation: str | None
    """Date de préparation au vêlage au format 'YYYY-MM-DD'."""

    calving_preparation_status: bool  # status de prepa vellage
    """"""

    calving_date: str | None
    """Date de vêlage au format 'YYYY-MM-DD'."""

    calving: bool  # status du vellage
    """"""
    abortion: bool
    """Avortement. True si un avortement a eu lieu, False sinon."""

    reproduction_details: str | None  # détails sur la reproduction
    """Détails sur la reproduction"""


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


class Setting(TypedDict):
    """Stocke des réglages utilisateur, en l'occurrence les durées de
    tarissement et de préparation au vêlage.

    :var dry_time: int, Temps de tarissement (en jour)
    :var calving_preparation_time: int, Temps de préparation au vêlage (en jour)
    """

    dry_time: int  # Temps de tarrisement (en jour)
    calving_preparation_time: int  # Temps de prepa vellage (en jour)

class Pharma_list_event(TypedDict):
    """
    Représente un événement lié à la pharmacie.

    :var date: str, Date de l'événement au format 'YYYY-MM-DD'
    :var medicaments: dict[str, int], Dictionnaire des médicaments , quantités.
    :var event_type: str, Type d'événement (par exemple, 'Traitement', 'prescription', 'sortie pour dlc').
    """
    date: str
    medicaments: dict[str, int]
    event_type: str