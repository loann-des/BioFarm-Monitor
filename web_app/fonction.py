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


def sum_pharma_in(year : int) -> dict[str,int]:
    from .models import get_all_prescription, Prescription
    res = {f"{x}" : 0 for x in get_pharma_liste()}
    prescription : Prescription
    for prescription in get_all_prescription():#TODO arranger avec années
        for care in prescription.traitement:
            medic = care.get("medicament")
            if quantite := care.get("quantite"):
                res[medic] += quantite
    return res

def sum_farma_used(year : int) -> dict[str,int]:
    # TODO sum_farma_used
    return None

def sum_calf_used(year : int) -> dict[str,int]:
    # TODO sum_calf_used
    return None

def sum_dlc_out(year : int) -> dict[str,int]:
    # TODO sum_calf_used
    return None
        
    

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

