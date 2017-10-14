from base64 import b64encode

from flask import json

from tests.base_test import BaseTest


class TestShoppingList(BaseTest):
    def test_add_shopping_list(self):
        """
        Test a Logged in User can add a shopping list into his/her account
        """
        response = self.client.post(
            "/v1/shoppinglists",
            data=json.dumps({
                "name": "Soko",
                "description": "Short Description About Soko"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(201, response.status_code)

    def test_view_shopping_lists(self):
        """
        Test a logged in user can view all his/her shoppinglists
         together with the items in them
        """
        self.create_shopping_lists("Family")
        self.create_shopping_lists("Games")

        self.create_shopping_lists_item("Wine", 2500, 3, "1")
        self.create_shopping_lists_item("Ball", 2500, 3, "2")

        response = self.client.get(
            "/v1/shoppinglists",
            headers=self.headers)
        self.assertEqual(2, len(json.loads(response.data)))

        x = json.loads(response.data)

        self.assertEqual(1, len(x[0]['items']))

    def test_user_can_query_for_a_shopping_list(self):
        """
                Test a logged in user can search for a shoppinglists
                """
        self.create_shopping_lists("Family")
        self.create_shopping_lists_item("Wine", 2500, 3, "Family")
        response = self.client.get(
            "/v1/shoppinglists?q=Family",
            headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_shopping_list_name_is_unique(self):
        """
        Test shopping_list cannot be added more than once
        """
        self.create_shopping_lists("Sons Birthday")

        response = self.client.post(
            "/v1/shoppinglists",
            data=json.dumps({
                "name": "Sons Birthday",
                "description": "Short Description About Sons Birthday"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(409, response.status_code)

    def test_unauthenticated_user_cannot_create_shopping_list(self):
        """
        Test a non Logged in User can not add a shopping list
        """
        response = self.client.post(
            "/v1/shoppinglists",
            data=json.dumps({
                "name": "Soko",
                "description": "Short Description About Soko"
            }),
            content_type='application/json')
        # 401 means user is un authenticated
        self.assertEqual(401, response.status_code)

    def test_update_shopping_list(self):
        """
        Test a Logged in User can Update his/her shopping lists
        """
        self.create_shopping_lists("Movies")
        response = self.client.put(
            "/v1/shoppinglists",
            data=json.dumps({
                "id": "1",
                "new_name": "Series",
                "description": "None"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_update_of_non_existing_shopping_list_fails(self):
        """
        Test a Logged in User can not Update a non existing shopping lists
        """
        response = self.client.put(
            "/v1/shoppinglists",
            data=json.dumps({
                "id": "100",  # Id that does not exist
                "new_name": "I Exist",
                "description": "None"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_delete_of_a_shopping_list(self):
        """
        Test a Logged in User Can Delete His/Her shopping lists
        """
        self.create_shopping_lists("Gaming")
        response = self.client.delete(
            "/v1/shoppinglists/1",
            content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_delete_of_non_existing_shopping_list_fails(self):
        """
        Test a Logged in User Can not Delete a non existing shopping lists
        """
        response = self.client.delete(
            "/v1/shoppinglists/900",
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_non_user_can_not_delete_a_shopping_list(self):
        """
        Test a Non Logged in User Can not Delete a shopping lists
        """
        self.create_shopping_lists("Morties")
        response = self.client.delete(
            "/v1/shoppinglists/1",
            content_type='application/json')  # No headers provided
        self.assertEqual(401, response.status_code)

    def test_user_can_share_shopping_list(self):
        """
        Test a Logged in User Can Share a shopping list with other users
        """
        self.create_shopping_lists("Shares")
        self.client.post("/v1/register",
                         data=json.dumps({"name": "tinyrick",
                                          "password": "python8",
                                          "email": "esir@gmail.com"
                                          }),
                         content_type='application/json')

        response = self.client.post(
            "/v1/shoppinglists/share",
            data=json.dumps({
                "id": "1",
                "email": "esir@gmail.com"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)
        headers2 = {
            'Authorization': 'Basic %s' %
                             b64encode(b"esir@gmail.com:python8")
                                 .decode("ascii")
        }
        res = self.client.get(
            "/v1/shoppinglists",
            data=json.dumps({
                "name": "Shares",
                "email": "esir@gmail.com"
            }),
            content_type='application/json', headers=headers2)
        self.assertEqual(1, len(json.loads(res.data)))

    def test_shopping_list_cannot_be_shared_with_non_app_users(self):
        self.create_shopping_lists("Shares")
        response = self.client.post(
            "/v1/shoppinglists/share",
            data=json.dumps({
                "id": "1",
                "email": "amnotthere@gmail.com"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_non_existing_shopping_list_cannot_be_shared(self):
        response = self.client.post(
            "/v1/shoppinglists/share",
            data=json.dumps({
                "id": "1",
                "email": "esir@gmail.com"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)
