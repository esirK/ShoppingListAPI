import unittest
from base64 import b64encode

from flask import json

from app import create_app, db


class TestMain(unittest.TestCase):
    def setUp(self):
        self.configurations = "testing"
        self.app = create_app(self.configurations)
        with self.app.app_context():
            self.client = self.app.test_client()  # create all tables
            db.drop_all()
            db.create_all()
            self.headers = {
                'Authorization': 'Basic %s' %
                                 b64encode(b"tinyrick@gmail.com:python")
                                     .decode("ascii")
            }
            self.client.post("/api/1_0/register",
                             data=json.dumps({"username": "tinyrick",
                                              "password": "python",
                                              "email": "tinyrick@gmail.com"
                                              }),
                             content_type='application/json')
            res = self.client.get("/api/1_0/token", headers=self.headers)
            token = json.loads(res.data)['token']
            self.token_headers = {
                'Authorization': 'Basic %s'
                                 % b64encode(bytes(token + ':', "utf-8"))
                                     .decode("ascii")
            }

    def test_user_registration(self):
        """Test if a user is created using the api"""
        response = self.client.post("/api/1_0/register",
                                    data=json.dumps({"username": "esirick",
                                                     "password": "python",
                                                     "email": "esimka@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            "Already Exists",
            self.client.post("/api/1_0/register",
                             data=json.dumps({"username": "esirick",
                                              "password": "python",
                                              "email": "esimka@gmail.com"
                                              }),
                             content_type='application/json').data.decode())
        response_no_arg = self.client.post("/api/1_0/register",
                                           data=json.dumps({"username": "esirick",
                                                            "password": "python",
                                                            "email": "  "
                                                            }),
                                           content_type='application/json')
        """
        Test if no arguments are passed the service aborts
        """
        self.assertEqual(400, response_no_arg.status_code)

    def test_verify_password(self):
        """
        Test if user is authenticated using email and password
        """
        res = self.client.get("/api/1_0/token", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data.decode())

    def test_authentication_with_token(self):
        """
        Test if user is authenticated using a valid token
        """
        res = self.client.get("/api/1_0/token", headers=self.token_headers)
        """Accessing Secure endpoint using a token"""
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data.decode())

    def test_user_login(self):
        """
        Test if A User Can Login With credentials he/she used to register with
        """
        response = self.client.post("/api/1_0/login",
                                    data=json.dumps({"password": "python",
                                                     "email": "tinyrick@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Loggedin", response.data.decode())

    def test_un_registered_user_cannot_login(self):
        """
        Test if A non User Can Login 
        """
        response = self.client.post("/api/1_0/login",
                                    data=json.dumps({"password": "python",
                                                     "email": "pickerick@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertIn("Does Not Exists", response.data.decode())

    def test_invalid_password(self):
        """
        Test Invalid Password Can Not Be used to login 
        """
        response = self.client.post("/api/1_0/login",
                                    data=json.dumps({"password": "y_python",
                                                     "email": "tinyrick@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertIn("Invalid Password", response.data.decode())

    def test_update_account(self):
        """
        Test If Account Is Updated Successfully
        """
        response = self.client.post("/api/1_0/update_account",
                                    data=json.dumps({"username": "EsirMkundi0",
                                                     "password": "python",
                                                     "email": "tinyrick@gmail.com"
                                                     }),
                                    content_type='application/json',
                                    headers=self.token_headers)
        self.assertIn("Details Updated Successfully", response.data.decode())
        """
        Test if no arguments are passed the service aborts
        """

        response_no_arg = self.client.post("/api/1_0/update_account",
                                           data=json.dumps({"username": "Esik",
                                                            "password": "  ",
                                                            "email": "tinyrick@gmail.com"
                                                            }),
                                           content_type='application/json',
                                           headers=self.token_headers)
        self.assertEqual(400, response_no_arg.status_code)

    def test_create_shopping_list(self):
        response = self.client.post("/api/1_0/create_shopping_list",
                                    data=
                                    json.dumps({"name": "Shopping List Ya Mum",
                                                "description":
                                                    "Things to "
                                                    "buy for mum on december"
                                                }),
                                    content_type='application/json',
                                    headers=self.token_headers)
        self.assertIn("ShoppingList Added Successfully",
                      response.data.decode())
        """
        Test if no arguments are passed the service aborts
        """
        response_no_args = self.client.post("/api/1_0/create_shopping_list",
                                            data=
                                            json.dumps({"name": "Shopping List Ya Mum",
                                                        "description": ""
                                                        }),
                                            content_type='application/json',
                                            headers=self.token_headers)
        self.assertEqual(400, response_no_args.status_code)

    def test_user_cannot_create_more_than_one_similar_shopping_lists(self):
        self.client.post("/api/1_0/create_shopping_list",
                         data=json.dumps({
                             "name": "Shopping List Ya Mum",
                             "description":
                                 "Things to "
                                 "buy for mum on december"}),
                         content_type='application/json',
                         headers=self.token_headers)
        response = self.client.post("/api/1_0/create_shopping_list",
                                    data=json.dumps({
                                        "name":
                                            "Shopping List Ya Mum",
                                        "description":
                                            "Things to "
                                            "buy for mum on december"
                                    }),
                                    content_type='application/json',
                                    headers=self.token_headers)
        self.assertIn("ShoppingList Already Exists", response.data.decode())


if __name__ == '__main__':
    unittest.main()
