import unittest
from base64 import b64encode

from flask import json

from app import create_app, db


class TestMain(unittest.TestCase):
    configurations = "testing"
    app = create_app(configurations)
    app.app_context().push()
    db.drop_all()
    db.create_all()

    def setUp(self):
        self.client = self.app.test_client()  # create all tables
        self.headers = {
            'Authorization': 'Basic %s' %
                             b64encode(b"tinyrick@gmail.com:python")
                                 .decode("ascii")
        }
        self.client.post("/v_1/register",
                         data=json.dumps({"name": "tinyrick",
                                          "password": "python",
                                          "email": "tinyrick@gmail.com"
                                          }),
                         content_type='application/json')
        res = self.client.get("/v_1/token", headers=self.headers)
        token = json.loads(res.data)['token']
        self.token_headers = {
            'Authorization': 'Basic %s'
                             % b64encode(bytes(token + ':', "utf-8"))
                                 .decode("ascii")
        }

    def test_user_registration(self):
        """Test if a user is created using the api"""
        response = self.client.post("/v_1/register",
                                    data=json.dumps({"name": "esirick",
                                                     "password": "morty",
                                                     "email": "esimorty@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            "Already Exists",
            self.client.post("/v_1/register",
                             data=json.dumps({"name": "esirick",
                                              "password": "python",
                                              "email": "esimorty@gmail.com"
                                              }),
                             content_type='application/json').data.decode())
        response_no_arg = self.client.post("/v_1/register",
                                           data=json.dumps({"name": "esirick",
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
        res = self.client.get("/v_1/token", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data.decode())

    def test_authentication_with_token(self):
        """
        Test if user is authenticated using a valid token
        """
        res = self.client.get("/v_1/token", headers=self.token_headers)
        """Accessing Secure endpoint using a token"""
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data.decode())

    def test_user_login(self):
        """
        Test If A Registered User Can Login to the app using registration
         credentials
        """
        self.client.post(
            "/v_1/register",
            data=json.dumps({"name": "esirick",
                             "password": "morty",
                             "email": "mortymorty@gmail.com"
                             }),
            content_type='application/json')
        response = self.client.post(
            "/v_1/login",
            data=json.dumps({
                "password": "morty",
                "email": "mortymorty@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(200, response.status_code)
        assert b'username' in response.data

    def test_user_can_not_login_with_invalid_creds(self):
        """
        Test If A Registered User Can Login to the app using
        Invalid Credentials
         """
        response = self.client.post(
            "/v_1/login",
            data=json.dumps({
                "password": "morty",
                "email": "tinyrick@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(401, response.status_code)
        assert b'Wrong Credentials' in response.data

    def test_un_registered_user_can_not_login(self):
        """
        Test If a Un Registered User Can Login to the app
         """
        response = self.client.post(
            "/v_1/login",
            data=json.dumps({
                "password": "morty",
                "email": "notregistered@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(401, response.status_code)
        assert b'No User Registered With' in response.data



if __name__ == '__main__':
    unittest.main()
