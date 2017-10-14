import unittest

from flask import json

from tests.base_test import BaseTest


class TestMain(BaseTest):

    def test_shopping_list_item_created_successfully(self):
        """
        Test a Logged In User Can Add items to their shopping_lists
        """
        self.create_shopping_lists("School")
        response = self.create_shopping_lists_item("Skuma", 10, 2, "1")
        print(response.data)
        self.assertEqual(201, response.status_code)

    def test_existing_shopping_list_item_can_not_be_created(self):
        """
        Test a Logged In User Can not Add an item more than once to 
        their shopping_lists
        """
        self.create_shopping_lists("Holiday")
        self.create_shopping_lists_item("Router", 2500, 24, "1")
        response = self.create_shopping_lists_item("Router", 2500, 24, "1")
        self.assertEqual(409, response.status_code)

    def test_shopping_list_not_found_returned(self):
        """
        Test 404 is returned on attempt to add items on non existing shoppinglist 
        :return: 
        """
        response = self.create_shopping_lists_item("Wounder Woman", 150, 2, "5")
        self.assertEqual(404, response.status_code)

    def test_un_authenticated_users_cannot_add_items(self):
        """
        Test non registered users not allowed to add shoppinglist items 
        """
        response = self.client.post(
            "/v1/shoppinglist_items",
            data=json.dumps({
                "name": "Amazing Woman",
                "price": "150",
                "quantity": "2",
                "shopping_list_id": "99"
            }
            ),
            content_type='application/json')  # authentication headers not passed
        self.assertEqual(401, response.status_code)

    def test_updating_shopping_list_items(self):
        """
        Test a Logged in User can update their shopping list items successfully
        """
        self.create_shopping_lists("Party")
        self.create_shopping_lists_item("Beer", 250, 24, "1")

        response = self.client.put(
            "/v1/shoppinglist_items",
            data=json.dumps({
                "id": "1",
                "new_name": "BeerX",
                "price": 0,
                "quantity": 0,
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
            "/v1/shoppinglist_items",
            data=json.dumps({
                "id": "10",
                "new_name": "Flask",
                "price": 0,
                "quantity": 0,
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
        self.create_shopping_lists_item("Beer", 250, 24, "1")

        response = self.client.put(
            "/v1/shoppinglist_items",
            data=json.dumps({
                "id": "1",
                "new_name": "Alcohol",
                "price": 0,
                "quantity": 0,
                "new_shopping_list_id": "51"
            }
            ),
            content_type='application/json', headers=self.headers)
        print(response.data)
        self.assertEqual(404, response.status_code)

    def test_delete_shopping_list_item(self):
        """
        tests if a logged in user is able to delete a shopping list item
        from his/her shopping lists
        """
        self.create_shopping_lists("BBQ")
        self.create_shopping_lists_item("Meat", 4000, 20, "1")
        response = self.delete_shopping_list_item(item_id="1")
        self.assertEqual(200, response.status_code)

    def test_delete_of_non_existing_shopping_list_item_fails(self):
        """
        tests response if a user tries to delete non-existing item
        """
        self.create_shopping_lists("Love")
        response = self.delete_shopping_list_item(item_id="10")
        self.assertEqual(404, response.status_code)

    def test_user_cannot_delete_an_item_from_non_existing_shopping_list(self):
        """
        Tests that a user is not able to delete an item from a shopping list
        that has not been created
        :return: 
        """
        response = self.delete_shopping_list_item(item_id="9")
        self.assertEqual(404, response.status_code)

    def test_non_authenticated_user_cannot_delete_an_item(self):
        response = self.client.delete(
            "/v1/shoppinglist_items",
            data=json.dumps({
                "id": "1"
            }),
            content_type='application/json')  # No Headers
        self.assertEqual(401, response.status_code)

    def delete_shopping_list_item(self, item_id):
        """
        Deletes a given shopping list item
        :return: 
        """
        return self.client.delete(
            "/v1/shoppinglist_items",
            data=json.dumps({
                "id": item_id
            }),
            content_type='application/json', headers=self.headers)


if __name__ == '__main__':
    unittest.main()
