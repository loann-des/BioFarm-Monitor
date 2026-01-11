#!/usr/bin/env python3
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "../"))

import unittest

from datetime import date, datetime, timedelta
from random import randint
from web_app.fonction import day_delta, first, format_bool_fr, last, my_strftime, parse_bool, parse_date, substract_date_to_str, sum_date_to_str

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
            lst = [randint(-100, 100) for j in range(i)]

            if len(lst) == 0:
                self.assertIsNone(first(lst))
            else:
                self.assertEqual(lst[0], first(lst))

    def test_last(self):
        for i in range(100):
            lst = [randint(-100, 100) for j in range(i)]

            if len(lst) == 0:
                self.assertIsNone(last(lst))
            else:
                self.assertEqual(lst[i-1], last(lst))

    def test_my_strftime(self):
        for i in range(100):
            d = random_date()
            dstr = my_strftime(d)
            expected = "{:04d}-{:02d}-{:02d}".format(d.year, d.month, d.day)

            self.assertEqual(expected, dstr)

    def test_parse_date(self):
        for i in range(100):
            d = random_date()
            dstr = "{:04d}-{:02d}-{:02d}".format(d.year, d.month, d.day)

            self.assertEqual(d, parse_date(dstr))

    # TODO: test date_to_str
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

class CaresUtilityFunctionsUnitTests:
    # TODO: test nb_cares_year
    def test_nb_cares_years(self):
        pass

    # TODO: test nb_cares_years_of_cow
    def test_nb_cares_years_of_cow(self):
        pass

    # TODO: test remaining_cares_on_year
    def test_remaining_care_on_year(self):
        pass

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
