import os
import csv
import io
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from werkzeug.datastructures import FileStorage
import openpyxl
from openpyxl.styles import Font, PatternFill
from io import BytesIO
from .models import (
    Cow,
    Prescription,
    Pharmacie,
    CowUntils,
    PrescriptionUntils,
    PharmacieUtils,
    Traitement,
    UserUtils,
)
import logging as lg

basedir = os.path.abspath(os.path.dirname(__file__))
URI = os.path.join(basedir, "txt")


def first(lst: List) -> Optional[object]:
    """Returns the first element of a list or None if the list is empty."""
    return lst[0] if lst else None


def last(lst: List) -> Optional[object]:
    """Returns the last element of a list or None if the list is empty."""
    return lst[-1] if lst else None


def strftime(date: date) -> str:
    return date.strftime('%d %B %Y')

def sum_date_to_str(date_from : date|str, delta_day :int) -> str :
    return strftime(
            date_from + timedelta(days=delta_day)
            if date_from.__class__ is date.__class__
            else datetime.strptime(date_from, "%d %B %Y").date() +  timedelta(days=delta_day)
            )

def substract_date_to_str(date_from : date|str, delta_day :int) -> str :
    return strftime(
            date_from - timedelta(days=delta_day)
            if date_from.__class__ is date.__class__
            else datetime.strptime(date_from, "%d %B %Y").date() -  timedelta(days=delta_day)
            )

def format_bool_fr(value: bool, true_str="Oui", false_str="Non") -> str:
    return true_str if value else false_str


def parse_date(date_str: str) -> Optional[date]:
    """Parses a date string in the format 'YYYY-MM-DD' and returns a date object
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

def pars_date(value : str)->date:
        return datetime.strptime(value, "%Y-%m-%d").date()

def parse_bool(value: str) -> Optional[bool]:
    if value is None or not value:
        return None
    return value.lower() in {"true", "1", "yes"}


def day_delta(date: date) -> int:
    """Calculates the number of days between the given date and the date one year ago from today.

    This function helps determine how many days have passed since a point exactly one year before the current date.

    Args:
        date (date): The date to compare.

    Returns:
        int: The number of days between the given date and one year ago from today.
    """
    today = datetime.now().date()  # date du jour
    # date d'il y a un ans jour pour jour
    one_year_ago = today - timedelta(days=365)
    return (date - one_year_ago).days


def nb_cares_years(user_id: int, cow_id) -> int:
    """Counts the number of care events for a cow in the past year by cow ID.

    This function retrieves all care records for the specified cow and returns the count of those that occurred within the last 365 days.

    Args:
        id (int): The unique identifier for the cow.

    Returns:
        int: The number of care events in the past year.
    """
    cares: List[Tuple[date, dict, str]] = CowUntils.get_care_by_id(user_id=user_id, cow_id=cow_id)
    return sum(
        day_delta(pars_date(care["date_traitement"])) <= 365 for care in cares
    )  # sum boolean if True 1 else 0


def nb_cares_years_of_cow(cow: Cow) -> int:
    """Counts the number of care events for a cow in the past year by cow object.

    This function examines the cow's care records and returns the count of those that occurred within the last 365 days.

    Args:
        cow (Cow): The cow object whose care records are to be counted.

    Returns:
        int: The number of care events in the past year.
    """
    cares: List[Traitement] = cow.cow_cares
    return sum(
        day_delta(pars_date(care["date_traitement"])) <= 365 for care in cares
    )  # sum boolean if True 1 else 0


def remaining_care_on_year(cow: Cow) -> int:
    """Calculates the number of remaining care treatments available for a cow in the current rolling year.

    This function determines how many care treatments a cow can still receive within a 365-day period, based on a maximum of three allowed treatments per year.

    Args:
        cow (Cow): The cow object whose remaining care treatments are to be calculated.

    Returns:
        int: The number of remaining care treatments for the cow in the current rolling year.
    """
    nb_care_year = nb_cares_years_of_cow(cow=cow)
    # traitement restant dans l'année glissante
    return 3 - nb_care_year


def new_available_care(cow: Cow) -> Optional[date]:
    """Determines the next date a cow becomes eligible for a new care treatment.

    This function calculates when a cow can receive its next care treatment based on its care history and the annual treatment limit.

    Args:
        cow (Cow): The cow object whose next available care date is to be determined.

    Returns:
        Optional[date]: The date when the cow is eligible for a new care treatment, or None if no care has been given.
    """

    nb_care_year = nb_cares_years_of_cow(cow=cow)

    if nb_care_year > 0 and len(cow.cow_cares) >= nb_care_year:
        # On prend la date du soin qui correspond à nb_care_year avant la fin de la liste
        care_date = pars_date(cow.cow_cares[-nb_care_year]["date_traitement"])
        return care_date + timedelta(days=365)
    elif len(cow.cow_cares) > 0:
        # Si il y a moins ou autant de soins que nb_care_year, on prend la date du premier soin
        return pars_date(cow.cow_cares[0]["date_traitement"]) + timedelta(days=365)
    else:
        # Pas de soins, donc pas de date dispo
        return None


def get_pharma_list(user_id) -> Optional[list[str]]:
    """Returns a list of all medication names available in the pharmacy.

    This function retrieves the pharmacy list and extracts the medication names from each care item.

    Returns:
        list[str]: A list of medication names.
    """

    return (
        pharma_list
        if (pharma_list := list(UserUtils.get_pharma_list(user_id)))
        else None
    )


def get_pharma_len(user_id: int) -> int:
    """Returns the number of medication available in the pharmacy.

    This function counts the total number of unique medications in the pharmacy list.

    Returns:
        int: The number of medication.
    """
    return len(pharma_list) if (pharma_list := get_pharma_list(user_id)) else 0


def sum_pharmacie_in(user_id: int,year: int) -> dict[str, int]:
    """Sums the quantities of each medication prescribed in a given year.

    This function iterates over all prescriptions for the specified year and accumulates the total quantity for each medication.

    Args:
        year (int): The year to sum medication prescriptions for.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total prescribed quantities for the year.
    """

    res = {f"{x}": 0 for x in get_pharma_list()}
    prescription: Prescription
    for prescription in PrescriptionUntils.get_year_prescription(user_id=user_id, year=year):
        for medic, quantity in prescription.care.items():
            res[medic] += quantity
    return res


def sum_pharmacie_used(user_id: int, year: int) -> dict[str, int]:
    """Sums the quantities of each medication actually used (administered to cows) in a given year.

    This function iterates over all care records for the specified year and accumulates the total quantity used for each medication.

    Args:
        year (int): The year to sum medication usage for.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total used quantities for the year.
    """

    res = {f"{x}": 0 for x in get_pharma_list(user_id=user_id)}
    cow_care: Tuple[date, dict, str]
    for cow_care in CowUntils.get_care_on_year(year):
        for medic, quantity in cow_care[1].items():
            res[medic] += quantity
    return res


def sum_calf_used(user_id: int, year: int) -> dict[str, int]:
    """Sums the quantities of each medication used for calves in a given year.

    This function iterates over all calf care records for the specified year and accumulates the total quantity used for each medication.

    Args:
        year (int): The year to sum medication usage for calves.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total used quantities for calves in the year.
    """

    res = {f"{x}": 0 for x in get_pharma_list()}
    cow_care: Tuple[date, dict[str, int], str]
    for cow_care in CowUntils.get_calf_care_on_year(user_id=user_id, year=year):
        for medic, quantity in cow_care[1].items():
            res[medic] += quantity
    return res


def sum_dlc_left(user_id: int, year: int) -> dict[str, int]:
    """Sums the quantities of each medication removed due to expired shelf life (DLC) in a given year.

    This function iterates over all medication removal records for expired DLC in the specified year and accumulates the total quantity removed for each medication.

    Args:
        year (int): The year to sum medication removals for expired DLC.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total quantities removed due to expired DLC for the year.
    """

    res = {f"{x}": 0 for x in get_pharma_list()}
    cow_care: Prescription
    for cow_care in PrescriptionUntils.get_dlc_left_on_year(user_id=user_id, year=year):
        for medic, quantity in cow_care.care.items():
            res[medic] += quantity
    return res


def sum_pharmacie_left(user_id: int, year: int) -> dict[str, int]:
    """Sums all medications taken out of the pharmacy cabinet in a given year.

    This function adds together the quantities of medications used (administered) and those removed due to expired shelf life (DLC) to give the total quantity of each medication taken out of the pharmacy for the year.

    Args:
        year (int): The year to sum all medication removals from the pharmacy.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total quantities taken out of the pharmacy for the year.
    """
    return dict(Counter(sum_pharmacie_used(user_id=user_id,year=year)) + Counter(sum_dlc_left(user_id=user_id, year=year)))


def remaining_pharmacie_stock(user_id: int, year: int) -> dict[str, int]:
    """Calculates the remaining stock of each medication in the pharmacy for a given year.

    This function computes the current year's stock by adding the medications prescribed this year and the previous year's remaining stock, then subtracting all medications taken out of the pharmacy this year.

    Args:
        year (int): The year for which to calculate the remaining pharmacy stock.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their remaining quantities for the year.
    """

    return dict(
        Counter(sum_pharmacie_in(user_id=user_id, year=year))
        + Counter(PharmacieUtils.get_pharmacie_year(user_id=user_id, year=year - 1).remaining_stock)
        - Counter(sum_pharmacie_left(user_id=user_id, year=year))
    )


def get_hystory_pharmacie(user_id : int) -> list[tuple[date, dict[str:int], str]]:
    """Builds a chronological history of all pharmacy-related events.

    This function combines care and prescription records, labels them, and returns a list sorted by date in descending order.

    Returns:
        list[tuple[date, dict[str:int], str]]: A list of tuples containing the date, medication dictionary, and event type label.
    """

    # Récupère les données
    care_raw = CowUntils.get_all_care(user_id=user_id) or []
    prescription_raw = PrescriptionUntils.get_all_prescription_cares() or []

    care_data = [(d, medics, f"care {id}") for d, medics, id in care_raw]
    prescription_data = [
        (d, medics, "dlc left" if dlc_left else "prescription")
        for d, medics, dlc_left in prescription_raw
    ]

    # Fusionne et trie par date décroissante
    full_history = care_data + prescription_data
    full_history.sort(key=lambda x: x[0], reverse=True)

    return full_history


def update_pharmacie_year(user_id : int, year: int) -> Pharmacie:
    """Updates or creates the pharmacy record for a given year with all relevant medication statistics.

    This function calculates and aggregates medication entries, usages, removals, and remaining stock for the specified year, then updates or creates the corresponding pharmacy record.

    Args:
        year (int): The year for which to update the pharmacy record.

    Returns:
        Pharmacie: The updated or newly created pharmacy record for the year.
    """

    total_enter = sum_pharmacie_in(user_id=user_id, year=year)
    total_used_calf = sum_calf_used(user_id=user_id, year=year)
    total_out_dlc = sum_dlc_left(user_id=user_id, year=year)
    total_used = sum_pharmacie_used(user_id=user_id, year=year)
    total_out = dict(Counter(total_used) + Counter(total_out_dlc))
    remaining_stock = dict(
        Counter(total_enter)
        + Counter(PharmacieUtils.get_pharmacie_year(user_id=user_id, year=year - 1).remaining_stock)
        - Counter(total_out)
    )
    pharmacie = Pharmacie(
        year_id=year,
        total_enter=total_enter,
        total_used=total_used,
        total_used_calf=total_used_calf,
        total_out_dlc=total_out_dlc,
        total_out=total_out,
        remaining_stock=remaining_stock,
    )
    return PharmacieUtils.updateOrDefault_pharmacie_year(user_id=user_id, year=year, default=pharmacie)


def pharmacie_to_csv(user_id: int, year: int) -> str:
    """Generates a CSV report of pharmacy medication statistics for a given year.

    This function compiles medication stock, usage, and prescription data into a CSV format, including previous year's stock and per-date prescription details.

    Args:
        year (int): The year for which to generate the pharmacy CSV report.

    Returns:
        str: The generated CSV content as a string.
    """

    pharmacie = update_pharmacie_year(user_id=user_id, year=year)

    # Liste des champs à exporter
    fields = [
        "remaining_stock_last_year",
        "total_enter",
        "total_used",
        "total_used_calf",
        "total_out_dlc",
        "total_out",
        "remaining_stock",
    ]

    # Récupère les données de l'année précédente
    prev_pharmacie = PharmacieUtils.get_pharmacie_year(user_id=user_id, year=year - 1)
    remaining_stock_last_year = getattr(prev_pharmacie, "remaining_stock", {})

    # Obtenir tous les médicaments à partir des données
    all_meds = sorted(get_pharma_list(user_id=user_id))

    output = io.StringIO()
    writer = csv.writer(output)

    # En-tête principale
    writer.writerow(["field"] + all_meds)

    # Ligne spéciale pour l’année précédente
    row = ["remaining_stock_last_year"]
    row.extend(remaining_stock_last_year.get(med, 0) for med in all_meds)
    writer.writerow(row)

    # === AJOUT : lignes des prescriptions par date ===
    # Construire dict : date_str -> med -> qty
    prescriptions_per_date = {
        pres.date.strftime("%d %b %Y"): pres.care
        for pres in PrescriptionUntils.get_year_prescription(year)
    }

    # Trier les dates
    sorted_dates = sorted(
        prescriptions_per_date.keys(), key=lambda d: datetime.strptime(d, "%d %b %Y")
    )

    # Écrire en CSV avec "prescription DATE" dans la première colonne pour bien identifier
    for date_str in sorted_dates:
        row = [date_str]
        row.extend(prescriptions_per_date[date_str].get(
            med, 0) for med in all_meds)
        writer.writerow(row)

    # === FIN AJOUT ===

    # Autres champs
    for field in fields[1:]:  # on saute 'remaining_stock_last_year' car déjà écrit
        row = [field]
        field_data = getattr(pharmacie, field, {})
        row.extend(field_data.get(med, 0) for med in all_meds)#TODO Verif le get
        writer.writerow(row)

    result = output.getvalue()
    print("CSV généré (pivoté + année précédente + prescriptions par date):\n", result)
    return result


def remaining_care_to_excel(user_id: int) -> bytes:
    """Generates an Excel file summarizing the remaining care treatments for each cow.

    This function creates an Excel spreadsheet listing each cow's ID, the number of remaining treatments, and the next renewal date, with color-coded formatting for easy interpretation.

    Returns:
        bytes: The Excel file content as a bytes object.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Traitements Restants"

    headers = ["Numéro Vache",
               "Nb Traitements Restants", "Date Renouvellement"]
    ws.append(headers)

    color_map = {
        3: "00FF00",  # vert
        2: "FFA500",  # orange
        1: "FF0000",  # rouge
        0: "000000",  # noir
    }

    cow: Cow
    for cow in CowUntils.get_all_cows(user_id=user_id):
        cow_id = cow.id
        nb_remaining = remaining_care_on_year(cow)
        renewal_date = new_available_care(cow)
        renewal_date_str = renewal_date.strftime(
            "%d %b %Y") if renewal_date else "N/A"

        ws.append([cow_id, nb_remaining, renewal_date_str])
        cell = ws.cell(row=ws.max_row, column=2)
        color = color_map.get(nb_remaining, "000000")

        # case coloré
        cell.fill = PatternFill(
            start_color=color, end_color=color, fill_type="solid")
        # texte en gras (optionnel)
        cell.font = Font(bold=True)

    # Envoi dans un buffer binaire
    excel_io = BytesIO()
    wb.save(excel_io)
    excel_io.seek(0)
    return excel_io


def get_all_dry_date(user_id: int) -> dict[int, date]:
    """Retrieves and sorts the dry dates for all cows with valid reproduction records.

    This function collects the 'dry' date for each cow and returns a dictionary sorted by date.

    Returns:
        dict[int, date]: A dictionary mapping cow IDs to their dry dates, sorted by date.
    """
    try:
        dry_dates = {
            cow_id: reproduction["dry"]
            for cow_id, reproduction in CowUntils.get_valide_reproduction(user_id=user_id).items()
            if not reproduction.get("dry_status", False)
        }
    except Exception as e:
        lg.error(f"Erreur lors de récupération des dates de tarisement : {e}")
        dry_dates = {}

    return dict(sorted(dry_dates.items(), key=lambda item: item[1]))


def get_all_calving_preparation_date(user_id: int) -> dict[int, date]:
    """Retrieves and sorts the calving preparation dates for all cows with valid reproduction records.

    This function collects the 'calving_preparation' date for each cow and returns a dictionary sorted by date.

    Returns:
        dict[int, date]: A dictionary mapping cow IDs to their calving preparation dates, sorted by date.
    """

    calving_preparation_dates = {
        cow_id: reproduction["calving_preparation"]
        for cow_id, reproduction in CowUntils.get_valide_reproduction(user_id=user_id).items()
        if not reproduction["calving_preparation_status"]
    }

    return dict(sorted(calving_preparation_dates.items(), key=lambda item: item[1]))


def get_all_calving_date(user_id: int) -> dict[int, date]:
    """Retrieves and sorts the calving dates for all cows with valid reproduction records.

    This function collects the 'calving_date' for each cow and returns a dictionary sorted by date.

    Returns:
        dict[int, date]: A dictionary mapping cow IDs to their calving dates, sorted by date.
    """

    calving_dates = {
        cow_id: reproduction["calving_date"]
        for cow_id, reproduction in CowUntils.get_valide_reproduction(user_id=user_id).items()
    }

    return dict(sorted(calving_dates.items(), key=lambda item: item[1]))


# def rename(pdf: FileStorage, img: FileStorage, article_id: int) -> tuple[str, str]:
#     # Extensions
#     pdf_ext = os.path.splitext(pdf.filename)[1] or ".pdf"
#     img_ext = os.path.splitext(img.filename)[1] or ".jpg"

#     # Noms automatiques
#     pdf_filename = f"blog-{article_id}{pdf_ext}"
#     img_filename = f"blog-{article_id}{img_ext}"

#     # Chemins complets
#     pdf_path = os.path.join('web_Page/static/pdf', pdf_filename)
#     img_path = os.path.join('web_Page/static/images/blog', img_filename)

#     # Sauvegarde
#     pdf.save(pdf_path)
#     img.save(img_path)

#     # Retourner les chemins relatifs depuis "static/"
#     return f"pdf/{pdf_filename}", f"images/blog/{img_filename}"
