import unittest
from base64 import b64encode

from flask import json

from app import create_app
from app.init_db import db


class BaseTest(unittest.TestCase):
    configurations = "testing"
    app = create_app(configurations)

    def setUp(self):
        with self.app.app_context():
            db.session.commit()
            db.drop_all()
            db.create_all()
            self.client = self.app.test_client()
            self.client.post("/v_1/register",
                             data=json.dumps({"name": "tinyrick",
                                              "password": "python8",
                                              "email": "tinyrick@gmail.com"
                                              }),
                             content_type='application/json')
            self.headers = {
                'Authorization': 'Basic %s' %
                                 b64encode(b"tinyrick@gmail.com:python8")
                                     .decode("ascii")
            }
            res = self.client.get("/v_1/token", headers=self.headers)
            token = json.loads(res.data)['token']
            self.token_headers = {
                'Authorization': 'Basic %s'
                                 % b64encode(bytes(token + ':', "utf-8"))
                                     .decode("ascii")
            }

    def create_shopping_lists(self, name):
        """
        Creates Shopping list with the Provided name
        :param name:
        """
        self.client.post(
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "" + name,
                "description": "Short Description About " + name + "Shopping List"
            }),
            content_type='application/json', headers=self.headers)

    def create_shopping_lists_item(self, name, price, quantity, shopping_list_name):
        """
        Creates a shopping list item with provided details
        :param name: Of the item
        :param price: of the item
        :param quantity: of the item
        :param shopping_list_name: to which the item belongs to
        :return: a response
        """
        return self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": name,
                "price": price,
                "quantity": quantity,
                "shopping_list_name": shopping_list_name,
            }
            ),
            content_type='application/json', headers=self.headers)