#!/usr/bin/env python3
import sys
sys.path.insert(1, "../")

import warnings

from datetime import datetime, date
from random import randint, sample
from web_app.views import app
from web_app.models import Cow, CowUntils, init_db, db

def test_add_cow(user_id: int, cow_id: int, birthdate: date):
    CowUntils.add_cow(user_id, cow_id, birthdate)

    if (c := Cow.query.get({"user_id": user_id, "cow_id" : cow_id})):
        assert c.user_id == user_id
        assert c.cow_id == cow_id
        assert c.cow_cares == []
        assert c.info == []
        assert c.in_farm == True
        assert c.born_date == birthdate
        assert c.reproduction == []
        assert c.is_calf == False
    else:
        raise ValueError("Failed to insert cow")

def test_get_cow(user_id: int, cow_id: int):
    birthdate = datetime.now().date()

    CowUntils.add_cow(user_id, cow_id, birthdate)

    if (c := CowUntils.get_cow(user_id, cow_id)):
        assert c.user_id == user_id
        assert c.cow_id == cow_id
        assert c.cow_cares == []
        assert c.info == []
        assert c.in_farm == True
        assert c.born_date == birthdate
        assert c.reproduction == []
        assert c.is_calf == False
    else:
        raise ValueError("Failed to get cow")

def test_get_all_cows():
    user_ids = sample([i for i in range(100)], 100)
    cow_ids = sample([i for i in range(100)], 100)
    birthdate = datetime.now().date()

    for i in range(100):
        CowUntils.add_cow(user_ids[i], cow_ids[i], birthdate)
    
    cs = CowUntils.get_all_cows()
    assert len(cs) == 100

    for i in range(len(cs)):
        assert cs[i].user_id == user_ids[i]
        assert cs[i].cow_id == cow_ids[i]
        assert cs[i].cow_cares == []
        assert cs[i].info == []
        assert cs[i].in_farm == True
        assert cs[i].born_date == birthdate
        assert cs[i].reproduction == []
        assert cs[i].is_calf == False

def test_update_cow(user_id, cow_id):
    CowUntils.add_cow(user_id, cow_id, None)

    if (c := Cow.query.get({"user_id": user_id, "cow_id" : cow_id})):
        assert c.user_id == user_id
        assert c.cow_id == cow_id
        assert c.cow_cares == []
        assert c.info == []
        assert c.in_farm == True
        assert c.born_date == None
        assert c.reproduction == []
        assert c.is_calf == False
    else:
        raise ValueError("Failed to insert cow")

    birthdate = datetime.now().date()

    CowUntils.update_cow(user_id, cow_id,
            cow_cares = [{
                "date_traitement": datetime.now().date(), 
                "medicaments": {"medicament", 1}, 
                "annotation": "Annotation"
            }],
            info = [{
                "date_note": birthdate,
                "information": "Information"
            }],
            in_farm = False,
            born_date = birthdate,
            reproduction = [{
                "insemination": birthdate,
                "ultrasound": True,
                "dry": birthdate,
                "dry_status": True,
                "calving_preparation": birthdate,
                "calving_preparation_status": True,
                "calving_date": birthdate,
                "calving": False,
                "abortion": False,
                "reproduction_details": "Details"
            }],
            is_calf = True)

    if (c := Cow.query.get({"user_id": user_id, "cow_id" : cow_id})):
        assert c.user_id == user_id
        assert c.cow_id == cow_id
        assert c.cow_cares == [{
                "date_traitement": datetime.now().date(), 
                "medicaments": {"medicament", 1}, 
                "annotation": "Annotation"
            }]
        assert c.info == [{
                "date_note": birthdate,
                "information": "Information"
            }]
        assert c.in_farm == False
        assert c.born_date == birthdate
        assert c.reproduction == [{
                "insemination": birthdate,
                "ultrasound": True,
                "dry": birthdate,
                "dry_status": True,
                "calving_preparation": birthdate,
                "calving_preparation_status": True,
                "calving_date": birthdate,
                "calving": False,
                "abortion": False,
                "reproduction_details": "Details"
            }]
        assert c.is_calf == True
    else:
        raise ValueError("Failed to insert cow")

def test_suppress_cow(user_id :int, cow_id: int):
    CowUntils.add_cow(user_id, cow_id, None)

    if (c := Cow.query.get({"user_id": user_id, "cow_id" : cow_id})):
        assert c.user_id == user_id
        assert c.cow_id == cow_id
        assert c.cow_cares == []
        assert c.info == []
        assert c.in_farm == True
        assert c.born_date == None
        assert c.reproduction == []
        assert c.is_calf == False
    else:
        raise ValueError("Failed to insert cow")
    
    CowUntils.suppress_cow(user_id, cow_id)

    assert Cow.query.get({"user_id": user_id, "cow_id" : cow_id}) is None

def test_remove_cow(user_id: int, cow_id: int):
    CowUntils.add_cow(user_id, cow_id, datetime.now().date())

    c = CowUntils.get_cow(user_id, cow_id)
    assert c.in_farm == True

    CowUntils.remove_cow(user_id, cow_id)

    c = CowUntils.get_cow(user_id, cow_id)
    assert c.in_farm == False

def test_add_calf(user_id, calf_id, birthdate):
    CowUntils.add_calf(user_id, calf_id, birthdate)

    if (c := Cow.query.get({"user_id": user_id, "cow_id" : calf_id})):
        assert c.user_id == user_id
        assert c.cow_id == calf_id
        assert c.cow_cares == []
        assert c.info == []
        assert c.in_farm == True
        assert c.born_date == birthdate
        assert c.reproduction == []
        assert c.is_calf == True
    else:
        raise ValueError("Failed to insert calf")

if (__name__ == "__main__"):
    warnings.simplefilter("ignore")

    with app.app_context():
        init_db()

        print("Test add cow", end="\t\t")
        for i in range(50):
            test_add_cow(randint(1, 9999), randint(1, 9999), None)
            test_add_cow(randint(1, 9999), randint(1, 9999), datetime.now().date())
        print("PASS")

        init_db()

        print("Test get cow", end="\t\t")
        for i in range(100):
            test_get_cow(randint(1, 9999), randint(1, 9999))
        print("PASS")

        # init_db()

        # print("Test update cow", end="\t\t")
        # for i in range(100):
        #     test_update_cow(randint(1, 9999), randint(1, 9999))
        # print("PASS")

        # init_db()

        # print("Test get all cows", end="\t")
        # test_get_all_cows()
        # print("PASS")

        init_db()

        print("Test suppress cow", end="\t")
        for i in range(100):
            test_suppress_cow(randint(1, 9999), randint(1, 9999))
        print("PASS")

        init_db()

        print("Test remove cow", end="\t\t")
        for i in range(100):
            test_remove_cow(randint(1, 9999), randint(1, 9999))
        print("PASS")

        init_db()

        print("Test add calf", end="\t\t")
        for i in range(50):
            test_add_calf(randint(1, 9999), randint(1, 9999), None)
            test_add_calf(randint(1, 9999), randint(1, 9999), datetime.now().date())
        print("PASS")
