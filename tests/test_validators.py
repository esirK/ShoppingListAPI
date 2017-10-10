from flask import json

from tests.base_test import BaseTest


class TestValidators(BaseTest):
    def test_un_available_end_point(self):
        """Tests what happens when a non existing endpoint is accessed"""
        response = self.client.get("/v_1/shop")

        self.assertEqual(True, self.is_json(response.data))

    def test_empty_shopping_lists_can_not_be_created(self):
        """Test a user can not create shopping lists with no name"""
        response = self.client.post(
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "   ",
                "description": "Short Description About Soko"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(400, response.status_code)

    def test_invalid_password(self):
        response = self.client.post(
            "/v_1/register",
            data=json.dumps({"name": "esirick",
                             "password": "morty",  # less than 6 characters
                             "email": "mortymorty@gmail.com"
                             }),
            content_type='application/json')
        self.assertEqual(400, response.status_code)

    def test_invalid_name(self):
        response = self.client.post(
            "/v_1/register",
            data=json.dumps({"name": "#*_#_#@(",  # Invalid Name
                             "password": "morty23",
                             "email": "mortymorty@gmail.com"
                             }),
            content_type='application/json')
        self.assertEqual(400, response.status_code)

    def is_json(self, data):
        try:
            json.loads(data)
        except ValueError:
            return False
        return True
