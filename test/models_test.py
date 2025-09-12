#!/usr/bin/env python3
import sys
sys.path.insert(1, "../")

import unittest
import warnings

from datetime import datetime, date
from random import randint, sample

from web_app.views import app
from web_app.models import Cow, CowUntils, init_db, db

class WebAppUnitTests(unittest.TestCase):
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

            CowUntils.add_cow(user_id, cow_id, birthdate)

            c = Cow.query.get({"user_id": user_id, "cow_id" : cow_id})
            self.assertIsNotNone(c)

            self.assertEqual(c.user_id, user_id)
            self.assertEqual(c.cow_id, cow_id)
            self.assertListEqual(c.cow_cares, [])
            self.assertListEqual(c.info, [])
            self.assertTrue(c.in_farm)
            self.assertEqual(c.born_date, birthdate)
            self.assertListEqual(c.reproduction, [])
            self.assertFalse(c.is_calf)

    def test_get_cow(self):
        init_db()

        for i in range(100):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)
            birthdate = None if i < 50 else datetime.now().date()

            CowUntils.add_cow(user_id, cow_id, birthdate)

            c = Cow.query.get({"user_id": user_id, "cow_id" : cow_id})
            self.assertIsNotNone(c)

            self.assertEqual(c.user_id, user_id)
            self.assertEqual(c.cow_id, cow_id)
            self.assertListEqual(c.cow_cares, [])
            self.assertListEqual(c.info, [])
            self.assertTrue(c.in_farm)
            self.assertEqual(c.born_date, birthdate)
            self.assertListEqual(c.reproduction, [])
            self.assertFalse(c.is_calf)

    # def test_get_all_cows(self):
    #     init_db()
    #
    #     user_ids = sample([i for i in range(100)], 100)
    #     cow_ids = sample([i for i in range(100)], 100)
    #     birthdate = datetime.now().date()
    #
    #     for i in range(100):
    #         CowUntils.add_cow(user_ids[i], cow_ids[i], birthdate)
    #
    #     cs = CowUntils.get_all_cows()
    #     self.assertEqual(len(cs), 100)
    #
    #     for i in range(len(cs)):
    #         self.assertEqual(cs[i].user_id, user_ids[i])
    #         self.assertEqual(cs[i].cow_id, cow_ids[i])
    #         self.assertListEqual(cs[i].cow_cares, [])
    #         self.assertListEqual(cs[i].info, [])
    #         self.assertTrue(cs[i].in_farm)
    #         self.assertEqual(cs[i].born_date, birthdate)
    #         self.assertListEqual(cs[i].reproduction, [])
    #         self.assertFalse(cs[i].is_calf == False)

    # def test_update_cow(self):
    #     init_db()
    #
    #     user_id = randint(1, 9999)
    #     cow_id = randint(1, 9999)
    #
    #     CowUntils.add_cow(user_id, cow_id, None)
    #
    #     c = Cow.query.get({"user_id": user_id, "cow_id" : cow_id})
    #     self.assertIsNotNone(c)
    #
    #     self.assertEqual(c.user_id, user_id)
    #     self.assertEqual(c.cow_id, cow_id)
    #     self.assertListEqual(c.cow_cares, [])
    #     self.assertListEqual(c.info, [])
    #     self.assertTrue(c.in_farm)
    #     self.assertIsNone(c.born_date)
    #     self.assertListEqual(c.reproduction, [])
    #     self.assertFalse(c.is_calf)
    #
    #     birthdate = datetime.now().date()
    #
    #     CowUntils.update_cow(user_id, cow_id,
    #             cow_cares = [{
    #                 "date_traitement": datetime.now().date(),
    #                 "medicaments": {"medicament", 1},
    #                 "annotation": "Annotation"
    #             }],
    #             info = [{
    #                 "date_note": birthdate,
    #                 "information": "Information"
    #             }],
    #             in_farm = False,
    #             born_date = birthdate,
    #             reproduction = [{
    #                 "insemination": birthdate,
    #                 "ultrasound": True,
    #                 "dry": birthdate,
    #                 "dry_status": True,
    #                 "calving_preparation": birthdate,
    #                 "calving_preparation_status": True,
    #                 "calving_date": birthdate,
    #                 "calving": False,
    #                 "abortion": False,
    #                 "reproduction_details": "Details"
    #             }],
    #             is_calf = True)
    #
    #     c = Cow.query.get({"user_id": user_id, "cow_id" : cow_id})
    #     self.assertIsNotNone(c)
    #
    #     self.assertEqual(c.user_id == user_id)
    #     self.assertEqual(c.cow_id == cow_id)
    #     self.assertListEqual(c.cow_cares, [{
    #             "date_traitement": datetime.now().date(),
    #             "medicaments": {"medicament", 1},
    #             "annotation": "Annotation"
    #         }])
    #     self.assertListEqual(c.info == [{
    #             "date_note": birthdate,
    #             "information": "Information"
    #         }])
    #     self.assertFalse(c.in_farm)
    #     self.assertEqual(c.born_date, birthdate)
    #     self.assertListEqual(c.reproduction, [{
    #             "insemination": birthdate,
    #             "ultrasound": True,
    #             "dry": birthdate,
    #             "dry_status": True,
    #             "calving_preparation": birthdate,
    #             "calving_preparation_status": True,
    #             "calving_date": birthdate,
    #             "calving": False,
    #             "abortion": False,
    #             "reproduction_details": "Details"
    #         }])
    #     self.assertTrue(c.is_calf)

    def test_remove_cow(self):
        init_db()

        user_id = randint(1, 9999)
        cow_id = randint(1, 9999)

        CowUntils.add_cow(user_id, cow_id, datetime.now().date())

        c = CowUntils.get_cow(user_id, cow_id)
        self.assertIsNotNone(c)
        self.assertTrue(c.in_farm)

        CowUntils.remove_cow(user_id, cow_id)

        c = CowUntils.get_cow(user_id, cow_id)
        self.assertIsNotNone(c)
        self.assertFalse(c.in_farm)

    def test_add_calf(self):
        init_db()

        for i in range(100):
            user_id = randint(1, 9999)
            calf_id = randint(1, 9999)
            birthdate = None if i < 50 else datetime.now().date()

            CowUntils.add_calf(user_id, calf_id, birthdate)

            c = Cow.query.get({"user_id": user_id, "cow_id" : calf_id})
            self.assertIsNotNone(c)

            self.assertEqual(c.user_id, user_id)
            self.assertEqual(c.cow_id, calf_id)
            self.assertListEqual(c.cow_cares, [])
            self.assertListEqual(c.info, [])
            self.assertTrue(c.in_farm)
            self.assertEqual(c.born_date, birthdate)
            self.assertListEqual(c.reproduction, [])
            self.assertTrue(c.is_calf)

if (__name__ == "__main__"):
    unittest.main()
