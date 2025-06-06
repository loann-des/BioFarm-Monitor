from datetime import date
import os
from typing import List, Tuple
from config import config as c
import enum
from .models import Cow, get_care_by_id
from werkzeug.datastructures import FileStorage
from .views import app
from datetime import datetime , timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
URI = os.path.join(basedir, 'txt')

def day_delta(date : date) -> int :
    today = datetime.now().date() # date du jour
    one_year_ago = today - timedelta(days=365) # date d'il y a un ans jour pour jour
    return (date - one_year_ago).days

def diff_dates(date1: date, date2: date) -> tuple[int, int, int]:
    """
    Retourne la différence exacte entre deux dates sous forme (années, mois, jours).
    """
    # if date1 > date2:
    #     date1, date2 = date2, date1  # Assurer que date1 est la plus ancienne

    # Différence brute
    annee = date2.year - date1.year
    mois = date2.month - date1.month
    jour = date2.day - date1.day

    # Ajustements si nécessaire
    if jour < 0:
        mois -= 1
        # nombre de jours du mois précédent
        from calendar import monthrange
        dernier_mois = date2.month - 1 or 12
        annee_temp = date2.year if date2.month > 1 else date2.year - 1
        jour += monthrange(annee_temp, dernier_mois)[1]

    if mois < 0:
        annee -= 1
        mois += 12

    return annee, mois, jour

def nb_cares_years(id : int) -> int:
    cares: List[Tuple[str, date, str]] = get_care_by_id(id=id)
    return sum(day_delta(care[1]) <= 365 for care in cares) # sum boolean if True 1 else 0
        
def nb_cares_years(cow : Cow) -> int:
    cares: List[Tuple[str, date, str]] = cow.traitement
    return sum(day_delta(care[1]) <= 365 for care in cares) # sum boolean if True 1 else 0
    
def get_pharma_liste() -> list[str] :
    from .models import get_pharma_liste as pharma
    return [care_item['medicament'] for care_item in pharma()]

def get_pharma_len() -> int :
    return len(get_pharma_liste())

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

app.jinja_env.globals.update(get_pharma_liste=get_pharma_liste)
app.jinja_env.globals.update(get_pharma_len=get_pharma_len)

