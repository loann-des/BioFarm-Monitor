import os
from typing import List
from config import config as c
import enum
from .models import Cow
from werkzeug.datastructures import FileStorage


basedir = os.path.abspath(os.path.dirname(__file__))
URI = os.path.join(basedir, 'txt')


def get_article(article_id: int) -> Cow:
    return Cow.query.get_or_404(article_id)


def get_AllArticle() -> list[Cow]:
    cows: List[Cow] = Cow.query.all()
    for x in cows:
        print(f"{x.id}, {x.race}, {x.date_naissance}, {x.traitement}")
    return Cow.query.all()

# def get_Autor(id) :
#     for x in Cow.query.filter(Cow.id.in_(id) ).all():
#         print(f"{x.id}, {x.nom}, {x.prenom}")#TODO remove print
#     return Cow.query.filter(Cow.id.in_(id) ).all()


def rename(pdf: FileStorage, img: FileStorage, article_id: int) -> tuple[str, str]:
    # Extensions
    pdf_ext = os.path.splitext(pdf.filename)[1] or ".pdf"
    img_ext = os.path.splitext(img.filename)[1] or ".jpg"

    # Noms automatiques
    pdf_filename = f"blog-{article_id}{pdf_ext}"
    img_filename = f"blog-{article_id}{img_ext}"

    # Chemins complets
    pdf_path = os.path.join('web_Page/static/pdf', pdf_filename)
    img_path = os.path.join('web_Page/static/images/blog', img_filename)

    # Sauvegarde
    pdf.save(pdf_path)
    img.save(img_path)

    # Retourner les chemins relatifs depuis "static/"
    return f"pdf/{pdf_filename}", f"images/blog/{img_filename}"
