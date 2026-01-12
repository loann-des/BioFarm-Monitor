#!/usr/bin/env python3
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "../"))

import unittest
import warnings

from datetime import datetime
from random import randint, sample
from web_app import app
from web_app.fonction import my_strftime
from web_app.models import Cow, CowUtils, init_db


class CowUtilsUnitTests(unittest.TestCase):
    """Test unitaires des fonctions membres de CowUtils.
    """

    def setUp(self):
        warnings.simplefilter("ignore")
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_add_cow(self):
        init_db()

        for i  in range(100):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)
            birthdate = None if i < 50 else datetime.now().date()

            CowUtils.add_cow(user_id, cow_id, birthdate)

            c : Cow = Cow.query.get({"user_id": user_id, "cow_id" : cow_id}) # type: ignore
            self.assertIsNotNone(c)

            self.assertEqual(c.user_id, user_id)
            self.assertEqual(c.cow_id, cow_id)
            self.assertListEqual(c.cow_cares, [])
            self.assertListEqual(c.info, [])
            self.assertTrue(c.in_farm)
            self.assertEqual(c.born_date, birthdate)
            self.assertListEqual(c.reproduction, [])
            self.assertFalse(c.is_calf)
            self.assertTrue(c.init_as_cow)

    def test_get_cow(self):
        init_db()

        for i in range(100):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)
            birthdate = None if i < 50 else datetime.now().date()

            CowUtils.add_cow(user_id, cow_id, birthdate)

            c : Cow = Cow.query.get({"user_id": user_id, "cow_id" : cow_id}) # type: ignore
            self.assertIsNotNone(c)

            self.assertEqual(c.user_id, user_id)
            self.assertEqual(c.cow_id, cow_id)
            self.assertListEqual(c.cow_cares, [])
            self.assertListEqual(c.info, [])
            self.assertTrue(c.in_farm)
            self.assertEqual(c.born_date, birthdate)
            self.assertListEqual(c.reproduction, [])
            self.assertFalse(c.is_calf)
            self.assertTrue(c.init_as_cow)

    def test_get_all_cows(self):
        init_db()

        user_ids = sample(list(range(100)), 100)
        cow_ids = sample(list(range(100)), 100)
        birthdate = datetime.now().date()

        for i in range(100):
            CowUtils.add_cow(user_ids[i], cow_ids[i], birthdate)

        cs : list[Cow] = CowUtils.get_all_cows()
        self.assertEqual(len(cs), 100)

        for i in range(len(cs)):
            self.assertEqual(cs[i].user_id, user_ids[i])
            self.assertEqual(cs[i].cow_id, cow_ids[i])
            self.assertListEqual(cs[i].cow_cares, [])
            self.assertListEqual(cs[i].info, [])
            self.assertTrue(cs[i].in_farm)
            self.assertEqual(cs[i].born_date, birthdate)
            self.assertListEqual(cs[i].reproduction, [])
            self.assertFalse(cs[i].is_calf)
            self.assertTrue(cs[i].init_as_cow)

    def test_get_all_cows_by_user(self):
        pass

    def test_update_cow(self):
        init_db()

        user_id = randint(1, 9999)
        cow_id = randint(1, 9999)

        CowUtils.add_cow(user_id, cow_id, None)

        c : Cow = Cow.query.get({"user_id": user_id, "cow_id" : cow_id}) # type: ignore
        self.assertIsNotNone(c)

        self.assertEqual(c.user_id, user_id)
        self.assertEqual(c.cow_id, cow_id)
        self.assertListEqual(c.cow_cares, [])
        self.assertListEqual(c.info, [])
        self.assertTrue(c.in_farm)
        self.assertIsNone(c.born_date)
        self.assertListEqual(c.reproduction, [])
        self.assertFalse(c.is_calf)
        self.assertTrue(c.init_as_cow)

        birthdate = datetime.now().date()

        CowUtils.update_cow(user_id, cow_id,
                cow_cares = [{
                    "date_traitement": my_strftime(datetime.now().date()),
                    "medicaments": {"medicament": 1},
                    "annotation": "Annotation"
                }],
                info = [{
                    "date_note": my_strftime(birthdate),
                    "information": "Information"
                }],
                in_farm = False,
                born_date = (birthdate),
                reproduction = [{
                    "insemination": my_strftime(birthdate),
                    "ultrasound": True,
                    "dry": my_strftime(birthdate),
                    "dry_status": True,
                    "calving_preparation": my_strftime(birthdate),
                    "calving_preparation_status": True,
                    "calving_date": my_strftime(birthdate),
                    "calving": False,
                    "abortion": False,
                    "reproduction_details": "Details"
                }],
                is_calf = True,
                init_as_cow = False)

        c = Cow.query.get({"user_id": user_id, "cow_id" : cow_id}) # type: ignore
        self.assertIsNotNone(c)

        self.assertEqual(c.user_id, user_id)
        self.assertEqual(c.cow_id, cow_id)
        self.assertListEqual(c.cow_cares, [{
                "date_traitement": my_strftime(datetime.now().date()),
                "medicaments": {"medicament": 1},
                "annotation": "Annotation"
            }])
        self.assertListEqual(c.info , [{
                "date_note": my_strftime(birthdate),
                "information": "Information"
            }])
        self.assertFalse(c.in_farm)
        self.assertEqual(c.born_date, birthdate)
        self.assertListEqual(c.reproduction, [{
                "insemination": my_strftime(birthdate),
                "ultrasound": True,
                "dry": my_strftime(birthdate),
                "dry_status": True,
                "calving_preparation": my_strftime(birthdate),
                "calving_preparation_status": True,
                "calving_date": my_strftime(birthdate),
                "calving": False,
                "abortion": False,
                "reproduction_details": "Details"
            }])
        self.assertTrue(c.is_calf)
        self.assertFalse(c.init_as_cow)

    def test_suppress_cow(self):
        init_db()

        user_ids = sample(list(range(100)), 100)
        cow_ids = sample(list(range(100)), 100)
        birthdate = datetime.now().date()

        for i in range(100):
            CowUtils.add_cow(user_ids[i], cow_ids[i], birthdate)

        cs = CowUtils.get_all_cows()

        self.assertEqual(len(cs), 100)

        for i in range(0, 100):
            j = randint(0, len(cs) - 1)

            self.assertEqual(cs[j].user_id, user_ids[j])
            self.assertEqual(cs[j].cow_id, cow_ids[j])

            CowUtils.suppress_cow(user_ids[j], cow_ids[j])
            cs = CowUtils.get_all_cows()

            self.assertRaises(ValueError, lambda : CowUtils.get_cow(user_ids[j],
                cow_ids[j]))

            del user_ids[j]
            del cow_ids[j]

    def test_remove_cow(self):
        init_db()

        user_id = randint(1, 9999)
        cow_id = randint(1, 9999)

        CowUtils.add_cow(user_id, cow_id, datetime.now().date())

        c = CowUtils.get_cow(user_id, cow_id)
        self.assertIsNotNone(c)
        self.assertTrue(c.in_farm)

        CowUtils.remove_cow(user_id, cow_id)

        c = CowUtils.get_cow(user_id, cow_id)
        self.assertIsNotNone(c)
        self.assertFalse(c.in_farm)

    def test_add_calf(self):
        init_db()

        for i in range(100):
            user_id = randint(1, 9999)
            calf_id = randint(1, 9999)
            birthdate = None if i < 50 else datetime.now().date()

            CowUtils.add_calf(user_id, calf_id, birthdate)

            c : Cow = Cow.query.get({"user_id": user_id, "cow_id" : calf_id}) # type: ignore
            self.assertIsNotNone(c)

            self.assertEqual(c.user_id, user_id)
            self.assertEqual(c.cow_id, calf_id)
            self.assertListEqual(c.cow_cares, [])
            self.assertListEqual(c.info, [])
            self.assertTrue(c.in_farm)
            self.assertEqual(c.born_date, birthdate)
            self.assertListEqual(c.reproduction, [])
            self.assertTrue(c.is_calf)

    def test_add_care(self):
        init_db()

        for _i in range(10):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)

            CowUtils.add_cow(user_id, cow_id)

            cow = CowUtils.get_cow(user_id, cow_id)
            self.assertEqual(0, len(cow.cow_cares))

            total_cares = 0

            for _j in range(10):
                if randint(0, 1) == 1:
                    total_cares += 1

                    medicname = "".join(
                        [chr(randint(33, 126)) for _ in range(10)])
                    dose = randint(1, 10000)
                    annotation = "".join(
                        [chr(randint(33, 126)) for _ in range(10)])

                    # XXX: Return value ignored for now. Use when
                    # remaining_care_on_year and new_available_care will be
                    # validated.
                    _ = CowUtils.add_care(cow, {
                        "date_traitement": my_strftime(datetime.now().date()),
                        "medicaments": {medicname: dose},
                        "annotation": annotation
                    })

                    self.assertEqual(my_strftime(datetime.now().date()),
                        cow.cow_cares[-1]["date_traitement"])
                    self.assertEqual({medicname: dose},
                        cow.cow_cares[-1]["medicaments"])
                    self.assertEqual(annotation,
                        cow.cow_cares[-1]["annotation"])

                self.assertEqual(total_cares, len(cow.cow_cares))

    def test_add_cow_care(self):
        init_db()

        for _i in range(10):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)

            CowUtils.add_cow(user_id, cow_id)
            self.assertEqual(0,
                len(CowUtils.get_cow(user_id, cow_id).cow_cares))

            total_cares = 0

            for _j in range(10):
                if randint(0, 1) == 1:
                    total_cares += 1

                    medicname = "".join(
                        [chr(randint(33, 126)) for _ in range(10)])
                    dose = randint(1, 10000)
                    annotation = "".join(
                        [chr(randint(33, 126)) for _ in range(10)])

                    # XXX: Return value ignored for now. Use when
                    # remaining_care_on_year and new_available_care will be
                    # validated.
                    _ = CowUtils.add_cow_care(user_id, cow_id, {
                        "date_traitement": my_strftime(datetime.now().date()),
                        "medicaments": {medicname: dose},
                        "annotation": annotation
                    })

                    cow = CowUtils.get_cow(user_id, cow_id)

                    self.assertEqual(my_strftime(datetime.now().date()),
                        cow.cow_cares[-1]["date_traitement"])
                    self.assertEqual({medicname: dose},
                        cow.cow_cares[-1]["medicaments"])
                    self.assertEqual(annotation,
                        cow.cow_cares[-1]["annotation"])

                self.assertEqual(total_cares,
                    len(CowUtils.get_cow(user_id, cow_id).cow_cares))

    # TODO: test update_cow_care
    def test_update_cow_care(self):
        pass

    # TODO: test delete_cow_care
    def test_delete_cow_care(self):
        pass

    # TODO: test geta_all_cares
    def test_get_all_cares(self):
        pass

    # TODO: test get_care_by_id
    def test_get_care_by_id(self):
        pass

    # TODO: test get_care_on_year
    def test_get_care_on_year(self):
        pass

    # TODO: test get_calf_care_on_year
    def test_get_calf_care_on_year(self):
        pass

class PrescriptionUtilsUnitTests(unittest.TestCase):
    # TODO: test add_prescription
    def test_add_prescription(self):
        pass

    # TODO: test add_dlc_left
    def test_add_dlc_left(self):
        pass

    # TODO: test get_all_prescriptions
    def test_get_all_prescriptions(self):
        pass

    # TODO: test get_all_prescriptions
    def test_get_all_prescriptions_cares(self):
        pass

    # TODO: test get_year_prescription
    def test_get_year_prescription(self):
        pass

    # TODO: test get_dlc_left_on_year
    def test_get_dlc_left_on_year(self):
        pass

class PharmacieUtilsUnitTests(unittest.TestCase):
    # TODO: test get_pharmacie_year
    def test_get_pharmacie_year(self):
        pass

    # TODO: test updateOrDefault_pharmacie_year
    def test_updateOrDefault_pharmacie_year(self):
        pass

    # TODO: test get_all_pharmacie
    def test_get_all_pharmacie(self):
        pass

    # TODO: test set_pharmacie_year
    def test_set_pharmacie_year(self):
        pass

    # TODO: test upload_pharmacie_year
    def test_upload_pharmacie_year(self):
        pass

class UserUtilsUnitTest(unittest.TestCase):
    # TODO: test add_user
    def add_user(self):
        pass

    # TODO: test set_user_setting
    def test_set_user_setting(self):
        pass

    # TODO: test get_user_setting
    def test_get_user_setting(self):
        pass

    # TODO: test get_user
    def test_get_user(self):
        pass

    # TODO: test add_medic_in_pharma_list
    def test_add_medic_in_pharma_list(self):
        pass

    # TODO: test get_pharma_list
    def test_get_pharma_list(self):
        pass

if (__name__ == "__main__"):
    unittest.main()
