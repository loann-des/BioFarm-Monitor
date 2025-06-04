from typing import List, Tuple
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import FileStorage
from sqlalchemy import Column, Integer, PickleType, String, Enum, DATE, URL, LargeBinary
from sqlalchemy.ext.mutable import MutableList
from datetime import datetime
import logging as lg
import enum

from .views import app

# Create database connection object
db = SQLAlchemy(app)

date = datetime.now()


class Race(enum.Enum):
    Brune = "Fiction"
    Holestine = "NonFiction"
    Normande = "Poetry"
    Other = "Other"


class Cow(db.Model):
    id = Column(Integer, primary_key=True)
    race = Column(Enum(Race), nullable=False)
    date_naissance = Column(DATE, nullable=False)
    traitement: List[Tuple[str, date]]
    traitement = Column(MutableList.as_mutable(PickleType),
                        default=list,
                        nullable=True
                        )

    def __init__(self, id, race, date_naissance, traitement):
        self.id = id
        self.race = race
        self.date_naissance = date_naissance
        self.traitement = traitement


def init_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    lg.warning("Database initialized!")


def upload_cow(id : int, race : Race, date_naissance : DATE, traitement):
    new_cow = Cow(
        id=id, race=race, date_naissance=date_naissance,traitement=traitement if traitement is not None else []
    )
    db.session.add(new_cow)
    db.session.commit()

