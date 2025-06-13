from collections import Counter
from datetime import date
import os
from typing import List, Optional, Tuple
from config import config as c
from .models import Cow,Prescription, get_care_by_id
from werkzeug.datastructures import FileStorage
from .views import app
from datetime import datetime, timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
URI = os.path.join(basedir, "txt")


def day_delta(date: date) -> int:
    """Calculates the number of days between the given date and the date one year ago from today.

    This function helps determine how many days have passed since a point exactly one year before the current date.

    Args:
        date (date): The date to compare.

    Returns:
        int: The number of days between the given date and one year ago from today.
    """
    today = datetime.now().date()  # date du jour
    one_year_ago = today - timedelta(days=365)  # date d'il y a un ans jour pour jour
    return (date - one_year_ago).days


def nb_cares_years(id: int) -> int:
    """Counts the number of care events for a cow in the past year by cow ID.

    This function retrieves all care records for the specified cow and returns the count of those that occurred within the last 365 days.

    Args:
        id (int): The unique identifier for the cow.

    Returns:
        int: The number of care events in the past year.
    """
    cares: List[Tuple[date, dict, str]] = get_care_by_id(id=id)
    return sum(
        day_delta(care[0]) <= 365 for care in cares
    )  # sum boolean if True 1 else 0


def nb_cares_years_of_cow(cow: Cow) -> int:
    """Counts the number of care events for a cow in the past year by cow object.

    This function examines the cow's care records and returns the count of those that occurred within the last 365 days.

    Args:
        cow (Cow): The cow object whose care records are to be counted.

    Returns:
        int: The number of care events in the past year.
    """
    cares: List[Tuple[date, dict, str]] = cow.cow_cares
    return sum(
        day_delta(care[0]) <= 365 for care in cares
    )  # sum boolean if True 1 else 0


def get_pharma_list() -> Optional[list[str]]:
    """Returns a list of all medication names available in the pharmacy.

    This function retrieves the pharmacy list and extracts the medication names from each care item.

    Returns:
        list[str]: A list of medication names.
    """
    from .models import get_pharma_list as pharma

    return pharma_list if (pharma_list := list(pharma().keys())) else None


def get_pharma_len() -> int:
    """Returns the number of medication available in the pharmacy.

    This function counts the total number of unique medications in the pharmacy list.

    Returns:
        int: The number of medication.
    """
    return len(pharma_list) if (pharma_list := get_pharma_list()) else 0
    

def sum_pharmacie_in(year: int) -> dict[str, int]:
    """Sums the quantities of each medication prescribed in a given year.

    This function iterates over all prescriptions for the specified year and accumulates the total quantity for each medication.

    Args:
        year (int): The year to sum medication prescriptions for.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total prescribed quantities for the year.
    """
    from .models import get_year_prescription, Prescription

    res = {f"{x}": 0 for x in get_pharma_list()}
    prescription: Prescription
    for prescription in get_year_prescription(year):
        for medic, quantity in prescription.care.items():
            res[medic] += quantity
    return res


def sum_pharmacie_used(year: int) -> dict[str, int]:
    """Sums the quantities of each medication actually used (administered to cows) in a given year.

    This function iterates over all care records for the specified year and accumulates the total quantity used for each medication.

    Args:
        year (int): The year to sum medication usage for.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total used quantities for the year.
    """
    from .models import get_care_on_year

    res = {f"{x}": 0 for x in get_pharma_list()}
    cow_care: Tuple[date, dict, str]
    for cow_care in get_care_on_year(year):
        for medic, quantity in cow_care[1].items():
            res[medic] += quantity
    return res


def sum_calf_used(year: int) -> dict[str, int]:
    return {}


def sum_dlc_left(year: int) -> dict[str, int]:
    """Sums the quantities of each medication removed due to expired shelf life (DLC) in a given year.

    This function iterates over all medication removal records for expired DLC in the specified year and accumulates the total quantity removed for each medication.

    Args:
        year (int): The year to sum medication removals for expired DLC.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total quantities removed due to expired DLC for the year.
    """
    from .models import get_dlc_left_on_year

    res = {f"{x}": 0 for x in get_pharma_list()}
    cow_care: Prescription
    for cow_care in get_dlc_left_on_year(year):
        for medic, quantity in cow_care.care.items():
            res[medic] += quantity
    return res


def sum_pharmacie_left(year: int) -> dict[str, int]:
    """Sums all medications taken out of the pharmacy cabinet in a given year.

    This function adds together the quantities of medications used (administered) and those removed due to expired shelf life (DLC) to give the total quantity of each medication taken out of the pharmacy for the year.

    Args:
        year (int): The year to sum all medication removals from the pharmacy.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their total quantities taken out of the pharmacy for the year.
    """
    return dict(Counter(sum_pharmacie_used(year)) + Counter(sum_dlc_left(year)))


def remaining_pharmacie_stock(year: int) -> dict[str, int]:
    """Calculates the remaining stock of each medication in the pharmacy for a given year.

    This function computes the current year's stock by adding the medications prescribed this year and the previous year's remaining stock, then subtracting all medications taken out of the pharmacy this year.

    Args:
        year (int): The year for which to calculate the remaining pharmacy stock.

    Returns:
        dict[str, int]: A dictionary mapping medication names to their remaining quantities for the year.
    """
    from .models import get_pharmacie_year

    return dict(
        Counter(sum_pharmacie_in(year))
        + Counter(get_pharmacie_year(year - 1).remaining_stock)
        - Counter(sum_pharmacie_left(year))
    )


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

app.jinja_env.globals.update(get_pharma_list=get_pharma_list)
app.jinja_env.globals.update(get_pharma_len=get_pharma_len)
