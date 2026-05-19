import logging as lg
import os

from datetime import date, datetime, timedelta
from typing import TypeVar

from .models.cow import Cow

from .models.type_dict import Reproduction, Setting, Traitement


basedir = os.path.abspath(os.path.dirname(__file__))
URI = os.path.join(basedir, "txt")

T = TypeVar("T")

def first(lst: list[T]) -> T | None:
    """Renvoie le premier élément d'une liste, ou None si la liste est vide."""
    return lst[0] if lst else None


def last(lst: list[T]) -> T | None:
    """Renvoie le dernier élément d'une liste, ou None si la liste est vide."""
    return lst[-1] if lst else None


def my_strftime(date_obj: date | str) -> str:
    """Convertit une date (objet date ou chaîne de caractères) en une chaîne de
    caractères au format "AAAA-MM-JJ".
    """
    return (date_obj if isinstance(date_obj, date)
                    else datetime.strptime(date_obj, "%Y-%m-%d").date()
            ).strftime('%Y-%m-%d')

def parse_date(date_obj: date | str) -> date:
    """Convertit une chaîne de caractère représentant une date au format
    "AAAA-MM-JJ" en un objet date.
    """
    return (date_obj if isinstance(date_obj, date)
            else datetime.strptime(date_obj, "%Y-%m-%d").date()
            )

def date_to_str(date_obj : date | str | None) -> str:
    """Convertit  une date ou une chaîne de caractère représentant une date
    au format "AAAA-MM-JJ" en une chaîne de caractère au format "JJ Mois AAA"
    (avec Mois le nom du mois dans la langue du système).
    """
    return (date_obj
            if isinstance(date_obj, date)
            else datetime.strptime(date_obj, "%Y-%m-%d").date()
            ).strftime('%d %B %Y') if date_obj else "Unknown"

def sum_date_to_str(date_obj: date | str, delta_day: int) -> str:
    """Ajoute le nombre de jours passé en argument à la date passée en
    arguments et renvoie le résultat sous la forme d'une chaîne de caractères
    au format "AAAA-MM-JJ".
    """
    return my_strftime(
                parse_date(date_obj) + timedelta(days=delta_day)
            )

def substract_date_to_str(date_obj: date | str, delta_day: int) -> str:
    """Soustrait le nombre de jours passé en argument à la date passée en
    arguments et renvoie le résultat sous la forme d'une chaîne de caractères
    au format "AAAA-MM-JJ".
    """
    return my_strftime(
                parse_date(date_obj) - timedelta(days=delta_day)
            )

def format_bool_fr(value: bool, true_str: str="Oui",
        false_str: str="Non") -> str:
    """Renvoie la transcription des booléens en termes français "Oui" et "Non".
    """
    return true_str if value else false_str

def format_bool_sexe(value: bool | None)-> str:
    """Renvoie la transcription des booléens en termes de sexe "Femelle" et "Mâle"."""
    if value is None:
        return "Unknown"
    return "Femelle" if value else "Mâle"

def parse_bool(value: str | None) -> bool | None:
    """Convertit une chaîne de caractères en booléen"""
    if value is None or not value:
        return None
    return value.lower() in {"true", "1", "yes"}

def day_delta(date: date) -> int:
    """Calcule le temps séparant la date d'il y a un an jour pour jour et la
    date fournie en argument.

    Cette fonction détermine le nombre de jours écoulés entre la date d'il y a
    un an jour pour jour et la date fournie en argument. Le résultat est négatif
    si la date fournie précède la date d'il y a un an, positif sinon.

    Arguments:
        * date (date): La date depuis laquelle on cherche à calculer le delta

    Renvoie:
        * int: le nombre de jours entre la date fournie en argument et la date
        un an jour pour jour avant aujourd'hui
    """
    today = datetime.now().date()  # date du jour
    # date d'il y a un ans jour pour jour
    one_year_ago = today - timedelta(days=365)
    return (date - one_year_ago).days

def nb_cares_years_of_cow(cow: Cow) -> int:
    """Compte le nombre de traitements administrés à une vache au cours de
    l'année passée.

    Cette fonction récupère toutes les entrées de l'historique des traitements
    de la vache représentée par l'objet Cow fourni en argument et renvoie le
    nombre de ces entrées datant des 365 derniers jours.

    Arguments:
        * cow (Cow): L'objet Cow représentant la vache

    Renvoie:
        * int: Le nombre de traitements administrés dans les 365 derniers jours
    """
    cares: list[Traitement] = cow.cow_cares
    return sum(
        day_delta(parse_date(care["date_traitement"])) >= 0 for care in cares
    )  # sum boolean if True 1 else 0

def remaining_care_on_year(cow: Cow) -> int:
    """Calcule le nombre de traitements qu'il est possible d'administrer à la
    vache dans le courant de l'année roulante actuelle.

    Cette fonction calcule le nombre de traitements que la vache représentée par
    l'objet Cow fourni en argument peut encore recevoir dans une période de 365
    jours, sur une base de trois traitements par an.

    Arguments:
        * cow (Cow): objet représentant la vache concernée

    Renvoie:
        * int: Le nombre de traitements que la vache peut encore recevoir dans
        le courant des 365 prochains jours.
    """
    nb_care_year = nb_cares_years_of_cow(cow=cow)
    # traitement restant dans l'année glissante
    return 3 - nb_care_year

def new_available_care(cow: Cow) -> date | None:
    """Calcule la prochaine date à partir de laquelle un nouveau traitement sera autorisé pour une vache.

    Cette fonction analyse l'historique des traitements sur l'année roulante
    pour déterminer, en fonction du quota annuel, à quelle date un prochain
    soin pourra être réalisé ou indique qu'aucune contrainte n'existe si aucun
    soin n'a encore été effectué.

    Arguments:
        * cow (Cow): La vache pour laquelle calculer la prochaine date de soin
        disponible.

    Renvoie:
        * date | None: La date à partir de laquelle un nouveau soin sera
        disponible, ou None s'il n'y a pas encore de traitements enregistrés.
    """
    nb_care_year = nb_cares_years_of_cow(cow=cow)

    if nb_care_year > 0 and len(cow.cow_cares) >= nb_care_year:
        # On prend la date du soin qui correspond à nb_care_year avant la fin de la liste
        cares_dates = sorted(cow.cow_cares, key=lambda x: parse_date(x["date_traitement"]))
        care_date = parse_date(cares_dates[-nb_care_year]["date_traitement"])

        return care_date + timedelta(days=365)
    elif len(cow.cow_cares) > 0:
        # Si il y a moins ou autant de soins que nb_care_year, on prend la date du premier soin
        return parse_date(cow.cow_cares[0]["date_traitement"]) + timedelta(days=365)
    else:
        # Pas de soins, donc pas de date dispo
        return None

def reload_reproduction_with(old: Reproduction, new: Reproduction, settings: Setting) -> Reproduction:
    """Recharge les données de reproduction d'une vache en tenant compte de
    l'historique des inséminations.

    Cette fonction analyse les données de reproduction d'une vache représentée
    par l'objet Cow fourni en argument, en particulier les dates d'insémination,
    pour mettre à jour les champs de reproduction tels que l'échographie, le
    tarissement, la préparation au vêlage, le vêlage et l'avortement en fonction
    des règles de gestion définies.

    Arguments:
        * cow (Cow): L'objet Cow représentant la vache dont les données de
        reproduction doivent être rechargées.
        * old (Reproduction): Les anciennes données de reproduction de la vache
        avant modification.
        * new (Reproduction): Les nouvelles données de reproduction de la vache
        après modification.
        * settings (Setting): Les réglages utilisateur, notamment les durées
        de tarissement et de préparation au vêlage.

    Renvoie:
        * Reproduction: Un nouvel objet Reproduction avec les données de reproduction mises à jour
        en fonction des inséminations enregistrées.
    """
    if len(new["insemination"]) > 1 and new["ultrasound"]:
        raise ValueError("Validation sur double insémination impossible.")
    if old["insemination"] != new["insemination"] and new["ultrasound"]:
        print(old["insemination"], " -> ",new["insemination"])
        new["calving_date"] = sum_date_to_str(new["insemination"][0], 280)
        new["dry"] = substract_date_to_str(new["calving_date"], settings["dry_time"])
        new["calving_preparation"] = substract_date_to_str(new["calving_date"], settings["calving_preparation_time"])
    return new