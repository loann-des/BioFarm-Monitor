#!/usr/bin/env python3
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "../"))

import unittest
import warnings

from datetime import date, datetime, timedelta
from random import randint
from web_app import app
from web_app.fonction import (
    day_delta,
    first,
    format_bool_fr,
    last,
    my_strftime,
    nb_cares_years,
    nb_cares_years_of_cow,
    parse_bool,
    parse_date,
    remaining_care_on_year,
    substract_date_to_str,
    sum_date_to_str
)
from web_app.models import CowUtils, init_db

def random_date():
    y = randint(1900, 2100)
    m = randint(1, 12)
    d = 0

    if m in [1, 3, 5, 7, 8, 10, 12]:
        d = randint(1, 31)
    elif m in [4, 6, 9, 11]:
        d = randint(1, 30)
    else:
        d = randint(1, 28)

    return date(y, m, d)

class DataFunctionsUnitTests(unittest.TestCase):
    def test_first(self):
        for i in range(100):
            lst = [randint(-100, 100) for _ in range(i)]

            if len(lst) == 0:
                self.assertIsNone(first(lst))
            else:
                self.assertEqual(lst[0], first(lst))

    def test_last(self):
        for i in range(100):
            lst = [randint(-100, 100) for _ in range(i)]

            if len(lst) == 0:
                self.assertIsNone(last(lst))
            else:
                self.assertEqual(lst[i-1], last(lst))

    def test_my_strftime(self):
        for _i in range(100):
            d = random_date()
            dstr = my_strftime(d)
            expected = "{:04d}-{:02d}-{:02d}".format(d.year, d.month, d.day)

            self.assertEqual(expected, dstr)

    def test_parse_date(self):
        for _i in range(100):
            d = random_date()
            dstr = "{:04d}-{:02d}-{:02d}".format(d.year, d.month, d.day)

            self.assertEqual(d, parse_date(dstr))

    def test_date_to_str(self):
        pass

    def test_sum_date_to_str(self):
        for i in range(100):
            start = random_date()
            delta = randint(-100, 100)
            end = start + timedelta(days=delta)

            start_str = my_strftime(start)
            expected = my_strftime(end)

            self.assertEqual(expected, sum_date_to_str(start, delta))
            self.assertEqual(expected, sum_date_to_str(start_str, delta))

    def test_substract_date_to_str(self):
        for i in range(100):
            start = random_date()
            delta = randint(-100, 100)
            end = start - timedelta(days=delta)

            start_str = my_strftime(start)
            expected = my_strftime(end)

            self.assertEqual(expected, substract_date_to_str(start, delta))
            self.assertEqual(expected, substract_date_to_str(start_str, delta))

    def test_format_bool_fr(self):
        self.assertEqual("Oui", format_bool_fr(True))
        self.assertEqual("Non", format_bool_fr(False))

    def test_parse_bool(self):
        self.assertEqual(True, parse_bool("True"))
        self.assertEqual(True, parse_bool("1"))
        self.assertEqual(True, parse_bool("yes"))

        self.assertEqual(False, parse_bool("False"))
        self.assertEqual(False, parse_bool("0"))
        self.assertEqual(False, parse_bool("no"))

    def test_day_delta(self):
        today = datetime.now().date()
        one_year_ago = today - timedelta(days = 365)
        one_year_ten_days_ago = today - timedelta(days = 375)

        delta = randint(0, 100)
        rand_delta_less = today - timedelta(days = (365 - delta))
        rand_delta_more = today - timedelta(days = (365 + delta))

        self.assertEqual(0, day_delta(one_year_ago))
        self.assertEqual(-10, day_delta(one_year_ten_days_ago))

        self.assertEqual(delta, day_delta(rand_delta_less))
        self.assertEqual(-delta, day_delta(rand_delta_more))

class CaresUtilityFunctionsUnitTests(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore")
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_nb_cares_years(self):
        init_db()

        for _i in range(10):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)

            CowUtils.add_cow(user_id, cow_id)

            cow = CowUtils.get_cow(user_id, cow_id)
            self.assertEqual(0, len(cow.cow_cares))

            medics_in_last_year = 0

            for j in range(10):
                last_medic_days = randint(0, 730)

                if last_medic_days <= 365:
                    medics_in_last_year += 1

                medic_date = datetime.now().date() - timedelta(days=last_medic_days)
                medic_name = "".join([chr(randint(33, 126)) for _ in range(10)])
                medic_amount = randint(1, 9999)
                annotation = "".join([chr(randint(33, 126)) for _ in range(10)])

                # XXX: Return value ignored for now. Use when
                # remaining_care_on_year and new_available_care will be
                # validated.
                _ = CowUtils.add_cow_care(user_id, cow_id, {
                    "date_traitement": my_strftime(medic_date),
                    "medicaments": {medic_name: medic_amount},
                    "annotation": annotation
                })

                cow = CowUtils.get_cow(user_id, cow_id)
                self.assertEqual(j + 1, len(cow.cow_cares))
                self.assertEqual(medics_in_last_year,
                    nb_cares_years(user_id, cow_id))

    def test_nb_cares_years_of_cow(self):
        init_db()

        for _i in range(10):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)

            CowUtils.add_cow(user_id, cow_id)

            cow = CowUtils.get_cow(user_id, cow_id)
            self.assertEqual(0, len(cow.cow_cares))

            medics_in_last_year = 0

            for j in range(10):
                last_medic_days = randint(0, 730)

                if last_medic_days <= 365:
                    medics_in_last_year += 1

                medic_date = datetime.now().date() - timedelta(days=last_medic_days)
                medic_name = "".join([chr(randint(33, 126)) for _ in range(10)])
                medic_amount = randint(1, 9999)
                annotation = "".join([chr(randint(33, 126)) for _ in range(10)])

                # XXX: Return value ignored for now. Use when
                # remaining_care_on_year and new_available_care will be
                # validated.
                _ = CowUtils.add_cow_care(user_id, cow_id, {
                    "date_traitement": my_strftime(medic_date),
                    "medicaments": {medic_name: medic_amount},
                    "annotation": annotation
                })

                cow = CowUtils.get_cow(user_id, cow_id)
                self.assertEqual(j + 1, len(cow.cow_cares))
                self.assertEqual(medics_in_last_year,
                    nb_cares_years_of_cow(cow))

    def test_remaining_care_on_year(self):
        init_db()

        for _i in range(10):
            user_id = randint(1, 9999)
            cow_id = randint(1, 9999)

            CowUtils.add_cow(user_id, cow_id)

            cow = CowUtils.get_cow(user_id, cow_id)

            self.assertEqual(0, len(cow.cow_cares))
            self.assertEqual(3, remaining_care_on_year(cow))

            remaining_cares = 3

            for j in range(10):
                last_medic_days = randint(0, 730)

                if remaining_cares <= 0:
                    last_medic_days = randint(366, 730)

                if last_medic_days <= 365:
                    remaining_cares -= 1

                medic_date = datetime.now().date() - timedelta(days=last_medic_days)
                medic_name = "".join([chr(randint(33, 126)) for _ in range(10)])
                medic_amount = randint(1, 9999)
                annotation = "".join([chr(randint(33, 126)) for _ in range(10)])

                # XXX: Return value ignored for now. Use when
                # remaining_care_on_year and new_available_care will be
                # validated.
                _ = CowUtils.add_cow_care(user_id, cow_id, {
                    "date_traitement": my_strftime(medic_date),
                    "medicaments": {medic_name: medic_amount},
                    "annotation": annotation
                })

                cow = CowUtils.get_cow(user_id, cow_id)
                self.assertEqual(j + 1, len(cow.cow_cares))
                self.assertEqual(remaining_cares, remaining_care_on_year(cow))

    # TODO: test new_available_care
    def test_new_available_care(self):
        pass

class PharmaUtilityFunctionsUnitTests:
    # TODO: test get_pharma_list
    def test_get_pharma_list(self):
        pass

    # TODO: test get_pharma_len
    def test_get_pharma_len(self):
        pass

    # TODO: test sum_pharmacie_len
    def test_sum_pharmacie_in(self):
        pass

    # TODO: test sum_pharmacie_used
    def test_sum_pharmacie_used(self):
        pass

    # TODO: test sum_calf_used
    def test_sum_calf_used(self):
        pass

    # TODO: test sum_dlc_left
    def test_sum_dlc_left(self):
        pass

    # TODO: test sum_pharmacie_left
    def test_sum_pharmacie_left(self):
        pass

    # TODO: test remaining_pharmacie_stock
    def test_remaining_pharmacie_stock(self):
        pass

    # TODO: test get_history_pharmacie
    def test_get_history_pharmacie(self):
        pass

    # TODO: test update_pharmacie_years
    def test_update_pharmacie_year(self):
        pass

    # TODO: test pharmacie_to_csv
    def test_pharmacie_to_csv(self):
        pass

    # TODO: test remaining_care_to_excel
    def test_remaining_care_to_excel(self):
        pass

class HerdUtilityFunctionsUnitTests:
    # TODO: test get_all_dry_date
    def test_get_all_dry_date(self):
        pass

    # TODO: test get_all_calving_preparation_date
    def test_get_all_calving_preparation_date(self):
        pass

    # TODO: test get_all_calving_date
    def test_get_all_calving_date(self):
        pass

if (__name__ == "__main__"):
    unittest.main()
