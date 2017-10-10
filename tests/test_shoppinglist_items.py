import unittest

from flask import json

from tests.base_test import BaseTest


class TestMain(BaseTest):

    def test_shopping_list_item_created_successfully(self):
        """
        Test a Logged In User Can Add items to their shopping_lists
        """
        self.create_shopping_lists("School")
        response = self.create_shopping_lists_item("Skuma", 10, 2, "School")
        self.assertEqual(201, response.status_code)

    def test_existing_shopping_list_item_can_not_be_created(self):
        """
        Test a Logged In User Can not Add an item more than once to 
        their shopping_lists
        """
        self.create_shopping_lists("Holiday")
        self.create_shopping_lists_item("Router", 2500, 24, "Holiday")
        response = self.create_shopping_lists_item("Router", 2500, 24, "Holiday")
        self.assertEqual(409, response.status_code)

    def test_shopping_list_not_found_returned(self):
        """
        Test 404 is returned on attempt to add items on non existing shoppinglist 
        :return: 
        """
        response = self.create_shopping_lists_item("Wounder Woman", 150, 2, "Movies")
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
        self.create_shopping_lists_item("Beer", 250, 24, "Party")

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
        self.create_shopping_lists_item("Beer", 250, 24, "Back to school")

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

    def test_delete_shopping_list_item(self):
        """
        tests if a logged in user is able to delete a shopping list item
        from his/her shopping lists
        """
        self.create_shopping_lists("BBQ")
        self.create_shopping_lists_item("Meat", 4000, 20, "BBQ")
        response = self.delete_shopping_list_item(name="Meat", shopping_list_name="BBQ")
        self.assertEqual(200, response.status_code)

    def test_delete_of_non_existing_shopping_list_item_fails(self):
        """
        tests response if a user tries to delete non-existing item
        """
        self.create_shopping_lists("Love")
        response = self.delete_shopping_list_item(name="Meat", shopping_list_name="Love")
        self.assertEqual(404, response.status_code)

    def test_user_cannot_delete_an_item_from_non_existing_shopping_list(self):
        """
        Tests that a user is not able to delete an item from a shopping list
        that has not been created
        :return: 
        """
        response = self.delete_shopping_list_item("Siko", "Pia Siko")
        self.assertEqual(404, response.status_code)

    def test_non_authenticated_user_cannot_delete_an_item(self):
        response = self.client.delete(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": "any name",
                "shopping_list_name": "Try me"
            }),
            content_type='application/json')  # No Headers
        self.assertEqual(401, response.status_code)

    def delete_shopping_list_item(self, name, shopping_list_name):
        """
        Deletes a given shopping list item
        :return: 
        """
        return self.client.delete(
            "/v_1/shoppinglist_items",
            data=json.dumps({
                "name": name,
                "shopping_list_name": shopping_list_name
            }),
            content_type='application/json', headers=self.headers)


if __name__ == '__main__':
    unittest.main()
