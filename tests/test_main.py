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
                'Authorization': 'Basic %s' % b64encode(b"tinyrick@gmail.com:python")
                    .decode("ascii")
            }
            self.client.post("/api/1_0/register",
                             data=json.dumps({"username": "tinyrick",
                                              "password": "python",
                                              "email": "tinyrick@gmail.com"
                                              }),
                             content_type='application/json')

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
        res = self.client.get("/api/1_0/token", headers=self.headers)
        token = json.loads(res.data)['token']
        token_headers = {
            'Authorization': 'Basic %s' % b64encode(bytes(token + ':', "utf-8")).decode("ascii")
        }
        res = self.client.get("/api/1_0/token", headers=token_headers)
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
        res = self.client.get("/api/1_0/token", headers=self.headers)
        token = json.loads(res.data)['token']
        token_headers = {
            'Authorization': 'Basic %s' % b64encode(bytes(token + ':', "utf-8")).decode("ascii")
        }
        response = self.client.post("/api/1_0/update_account",
                                    data=json.dumps({"username": "EsirMkundi0",
                                                     "password": "python",
                                                     "email": "tinyrick@gmail.com"
                                                     }),
                                    content_type='application/json', headers=token_headers)
        self.assertIn("Details Updated Successfully", response.data.decode())


if __name__ == '__main__':
    unittest.main()
