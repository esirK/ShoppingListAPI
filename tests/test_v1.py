import unittest
from base64 import b64encode

from flask import json

from app import create_app, db


class TestMain(unittest.TestCase):
    configurations = "testing"
    app = create_app(configurations)
    app.app_context().push()
    # create all tables
    db.drop_all()
    db.create_all()

    def setUp(self):
        self.client = self.app.test_client()
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
                             "password": "morty",
                             "email": "mortymorty@gmail.com"
                             }),
            content_type='application/json')
        response = self.client.post(
            "/v_1/user",
            data=json.dumps({
                "password": "morty",
                "email": "mortymorty@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(200, response.status_code)

    def test_user_can_not_login_with_invalid_creds(self):
        """
        Test If A Registered User Can Login to the app using
        Invalid Credentials
         """
        # email "tinyrick@gmail.com" was created on setup but with 'python' as the pass
        response = self.client.post(
            "/v_1/user",
            data=json.dumps({
                "password": "morty",
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
                "password": "morty",
                "email": "notregistered@gmail.com"
            }),
            content_type='application/json')
        self.assertEqual(401, response.status_code)

    def test_add_shopping_list(self):
        """
        Test a Logged in User can add a shopping list into his/her account
        """
        response = self.client.post(
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "Soko",
                "description": "Short Description About Soko"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(201, response.status_code)

    def test_shopping_list_name_is_unique(self):
        """
        Test shopping_list cannot be added more than once
        """
        self.create_shopping_lists("Sons Birthday")

        response = self.client.post(
            "/v_1/shoppinglists",
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
            "/v_1/shoppinglists",
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
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "Movies",
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
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "I Don't Exist",
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
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "Gaming"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_delete_of_non_existing_shopping_list_fails(self):
        """
        Test a Logged in User Can not Delete a non existing shopping lists 
        """
        response = self.client.delete(
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "Not existing"
            }),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_non_user_can_not_delete_a_shopping_list(self):
        """
        Test a Non Logged in User Can not Delete a shopping lists 
        """
        self.create_shopping_lists("Morties")
        response = self.client.delete(
            "/v_1/shoppinglists",
            data=json.dumps({
                "name": "Morties"
            }),
            content_type='application/json')  # No headers provided
        self.assertEqual(401, response.status_code)

    def test_shopping_list_item_created_successfully(self):
        """
        Test a Logged In User Can Add items to their shopping_lists
        """
        self.create_shopping_lists("School")
        response = self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Skuma",
                "price": "10",
                "quantity": "2",
                "shopping_list_name": "School"
            }
            ),
            content_type='application/json', headers=self.headers)
        self.assertEqual(201, response.status_code)

    def test_existing_shopping_list_item_can_not_be_created(self):
        """
        Test a Logged In User Can not Add an item more than once to 
        their shopping_lists
        """
        self.create_shopping_lists("Holiday")
        self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Router",
                "price": "2500",
                "quantity": "24",
                "shopping_list_name": "Holiday"
            }
            ),
            content_type='application/json', headers=self.headers)
        response = self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Router",
                "price": "250",
                "quantity": "24",
                "shopping_list_name": "Holiday"
            }
            ),
            content_type='application/json', headers=self.headers)
        self.assertEqual(409, response.status_code)

    def test_shopping_list_not_found_returned(self):
        """
        Test 404 is returned on attempt to add items on non existing shoppinglist 
        :return: 
        """
        response = self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Wounder Woman",
                "price": "150",
                "quantity": "2",
                "shopping_list_name": "Movies"
            }
            ),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_un_authenticated_users_cannot_add_items(self):
        """
        Test non registered users not allowed to add shoppinglist items 
        """
        response = self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Amazing Woman",
                "price": "150",
                "quantity": "2",
                "shopping_list_name": "Movies"
            }
            ),
            content_type='application/json')  # authentication headers not passed
        self.assertEqual(401, response.status_code)

    def test_updating_shopping_list_items(self):
        """
        Test a Logged in User can update their shopping list items successfully
        """
        self.create_shopping_lists("Party")
        self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Beer",
                "price": "250",
                "quantity": "24",
                "shopping_list_name": "Party"
            }
            ),
            content_type='application/json', headers=self.headers)

        response = self.client.put(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Beer",
                "new_name": "BeerX",
                "price": 0,
                "quantity": 0,
                "shopping_list_name": "Party",
                "new_shopping_list_name": "None"
            }
            ),
            content_type='application/json', headers=self.headers)
        self.assertEqual(200, response.status_code)

    def test_user_can_not_update_non_existing_item(self):
        """
        Tests if a User Can Update a Non-existing item in their shopping lists
        """
        self.create_shopping_lists("Fictions")
        response = self.client.put(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Flash",
                "new_name": "Flask",
                "price": 0,
                "quantity": 0,
                "shopping_list_name": "Fiction",
                "new_shopping_list_name": "None"
            }
            ),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_user_can_not_update_item_to_non_existing_shopping_list(self):
        """
        Tests updating an item in one shopping list to a shopping list
        that does not exist fails
        """
        self.create_shopping_lists("Back to school")
        self.client.post(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Beer",
                "price": "250",
                "quantity": "24",
                "shopping_list_name": "Back to school"
            }
            ),
            content_type='application/json', headers=self.headers)

        response = self.client.put(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "Beer",
                "new_name": "Alcohol",
                "price": 0,
                "quantity": 0,
                "shopping_list_name": "Back to school",
                "new_shopping_list_name": "Fiction"
            }
            ),
            content_type='application/json', headers=self.headers)
        self.assertEqual(404, response.status_code)

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


if __name__ == '__main__':
    unittest.main()
