from flask import json

from tests.base_test import BaseTest


class TestAuthentication(BaseTest):
    def test_user_registration(self):
        """Test if a user is created using the api"""
        response = self.client.post("/v_1/register",
                                    data=json.dumps({"name": "esirick",
                                                     "password": "morty11",
                                                     "email": "esimorty@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn(
            "Already Exists",
            self.client.post("/v_1/register",
                             data=json.dumps({"name": "esirick",
                                              "password": "python8",
                                              "email": "esimorty@gmail.com"
                                              }),
                             content_type='application/json').data.decode())
        response_no_arg = self.client.post("/v_1/register",
                                           data=json.dumps({"name": "esirick",
                                                            "password": "python8",
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

    def test_authentication_with_token(self):
        """
        Test if user is authenticated using a valid token
        """
        res = self.client.get("/v_1/token", headers=self.token_headers)
        """Accessing Secure endpoint using a token"""
        self.assertEqual(res.status_code, 200)

    def test_user_login(self):
        """
        Test If A Registered User Can Login to the app using registration
         credentials
        """
        self.client.post(
            "/v_1/register",
            data=json.dumps({"name": "esirick",
                             "password": "morty00",
                             "email": "mortymorty@gmail.com"
                             }),
            content_type='application/json')
        response = self.client.post(
            "/v_1/user",
            data=json.dumps({
                "password": "morty00",
                "email": "mortymorty@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(200, response.status_code)

    def test_user_update(self):
        """Test a logged in user can update their account details"""
        response = self.client.put(
            "/v_1/user",
            data=json.dumps({
                "name": "Kamaku",
                "password": "None"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)
        self.assertIn("Kamaku", json.loads(response.data)["User"]["username"])

    def test_user_can_not_login_with_invalid_creds(self):
        """
        Test If A Registered User Can Login to the app using
        Invalid Credentials
         """
        # email "tinyrick@gmail.com" was created on setup but with 'python8' as the pass
        response = self.client.post(
            "/v_1/user",
            data=json.dumps({
                "password": "morty00",
                "email": "tinyrick@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(401, response.status_code)

    def test_un_registered_user_can_not_login(self):
        """
        Test If a Un Registered User Can Login to the app
         """
        response = self.client.post(
            "/v_1/user",
            data=json.dumps({
                "password": "morty00",
                "email": "notregistered@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(401, response.status_code)
