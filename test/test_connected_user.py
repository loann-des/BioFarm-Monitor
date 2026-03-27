#!/usr/bin/env python3
import os
import sys

from web_app.models import init_db_test
from web_app.connnected_user_web.connected_user import ConnectedUser
from web_app.models.cow import CowUtils
from web_app.models.user import UserUtils, Users
from web_app.fonction import my_strftime
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "../"))
from web_app import app

import unittest
import warnings

from random import randint
from datetime import date, datetime, timedelta



def random_date():
    y = randint(1900, 2100)
    m = randint(1, 12)
    d = 0

    if m in {1, 3, 5, 7, 8, 10, 12}:
        d = randint(1, 31)
    elif m in {4, 6, 9, 11}:
        d = randint(1, 30)
    else:
        d = randint(1, 28)

    return date(y, m, d)

def init_users(nb_user : int):
    for i in range(nb_user):
        UserUtils.add_user(email=f'user{i}@mail.com',password=str(hash(i)))

class TestConnectedUser(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore")
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        
    def test_nb_cares_years(self):
        init_db_test()
        init_users(100)
        users : dict[int, list[int]] = {}

        
        for _i in range(10):
            user_id = randint(1, 100)
            if user_id not in users:
                users[user_id] = []
            cow_id = randint(1, 9999)
            while cow_id in users[user_id] :
                cow_id = randint(1, 9999)
            users[user_id].append(cow_id)

            CowUtils.add_cow(user_id, cow_id)

            cow = CowUtils.get_cow(user_id, cow_id)
            self.assertEqual(0, len(cow.cow_cares))
            user : Users = UserUtils.get_user(user_id=user_id)
            connected_user : ConnectedUser = ConnectedUser(user=user)
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
                    connected_user.nb_cares_years(cow_id))

    def test_get_pharma_list(self):
        init_db_test()
        init_users(100)
        pharma_list : dict[int, list[str]]= {}

        
        for i in range(10):
            user_id = randint(1, 100)
            if user_id not in pharma_list:
                pharma_list[user_id] = []
            user : Users = UserUtils.get_user(user_id=user_id)
            connected_user : ConnectedUser = ConnectedUser(user=user)
            

            for j in range(10):

                medic_name = "".join([chr(randint(33, 126)) for _ in range(10)])
                pharma_list[user_id].append(medic_name)
                UserUtils.add_medic_in_pharma_list(user_id=user_id, medic=medic_name,mesur='ml')

                self.assertEqual(len(pharma_list[user_id]), len(connected_user.get_pharma_list()))
                self.assertListEqual(pharma_list[user_id],
                    connected_user.get_pharma_list())    
    def test_get_pharma_len(self):
        init_db_test()
        init_users(100)
        pharma_list : dict[int, int]= {}

        
        for i in range(10):
            user_id = randint(1, 100)
            if user_id not in pharma_list:
                pharma_list[user_id] = 0
            user : Users = UserUtils.get_user(user_id=user_id)
            connected_user : ConnectedUser = ConnectedUser(user=user)
            

            for j in range(10):

                medic_name = "".join([chr(randint(33, 126)) for _ in range(10)])
                UserUtils.add_medic_in_pharma_list(user_id=user_id, medic=medic_name,mesur='ml')
                pharma_list[user_id]+= 1

                self.assertEqual(pharma_list[user_id], connected_user.get_pharma_len())
       
    def test_sum_pharmacie_in(self):
        pass    
    
    def test_sum_pharmacie_used(self):
        pass    
    
    def test_sum_calf_used(self):
        pass    
    
    def test_sum_dlc_left(self):
        pass    
    
    def test_sum_pharmacie_left(self):
        pass    
    
    def test_remaining_pharmacie_stock(self):
        pass    
    
    def test_get_history_pharmacie(self):
        pass
    
    def test_update_pharmacie_year(self):
        pass
    
    def test_pharmacie_to_csv(self):
        pass
    
    def test_remaining_care_to_excel(self):
        pass
    
    def test_get_all_dry_date(self):
        pass
    
    def test_get_all_calving_preparation_date(self):
        pass
    
    def test_get_all_calving_date(self):
        pass



if __name__ == "__main__":
    unittest.main()
