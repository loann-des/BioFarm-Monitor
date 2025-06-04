from flask import Flask

from .views import app
from .models import db
from .fonction import *


@app.cli.command("init_db")
def init_db():
    models.init_db()
    
@app.cli.command("get_all")
def get_all():
    print(fonction.get_AllArticle())
