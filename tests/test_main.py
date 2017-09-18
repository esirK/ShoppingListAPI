import unittest

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

    def test_user_registration(self):
        """Test if a user is created using the api"""
        response = self.client.post("/api/1_0/register",
                                    data=json.dumps({"username": "esirick",
                                                     "password": "python",
                                                     "email": "esimka@gmail.com"
                                                     }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
