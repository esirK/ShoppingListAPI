[![Build Status](https://travis-ci.org/esirK/ShoppingListAPI.svg?branch=user)](https://travis-ci.org/esirK/ShoppingListAPI)
[![Coverage Status](https://coveralls.io/repos/github/esirK/ShoppingListAPI/badge.svg?branch=user)](https://coveralls.io/github/esirK/ShoppingListAPI?branch=user)
[![Code Health](https://landscape.io/github/esirK/ShoppingListAPI/user/landscape.svg?style=flat)](https://landscape.io/github/esirK/ShoppingListAPI/user)
# ShoppingList API
Shopping List API is a flask API that allows clients to Interact with the Shopping List App that allows users to create shopping lists, manage them as well as share them
 as a web service.

# installation procedure.
  1. Ensure you have *python 3 >*, *postgresql*, *pip*, and *virtualenv* installed on your local machine.
  2. Make a directory for the App and Clone the repo from *https://github.com/esirK/ShoppingListAPI.git*
  3. Create a virtual environment `virtualenv anyname`
  4. Install all requirements from requirements.txt through `pip install requirements.txt`
  5. Export the following variables
  ```
  export SECRET_KEY="very_secret_key"
  export CURRENT_CONFIG="development"
  export DB="postgresql:///my_db"
  export TESTDB="postgresql:///test_db"
  export PRODUCTIONDB="postgresql:///production_db"
  ```
  6. you are supposed to create a postgres database similar to your `DB` *export*
  7. For hands on testing, REST client tools like *postman* can be used

# Running the app
  1. `python run.py runserver`

#### For interacting with the app in shell mode run
      `python run.py shell`
#### For running tests
      At root of the shopping list Api folder run `- nosetests --with-coverage --cover-inclusive --cover-package=app`

### Api endpoints

| url | Method|  Description| Authentication |
| --- | --- | --- | --- |
| /register | POST | Allow new user to register | FALSE
| /user | POST | Allow a Registered user to login and get user details | FALSE
| /token | GET | get Authentication token for use on next requests | TRUE
| /user | PUT | Update user details | TRUE
| /shoppinglists{q} | GET | Get shopping list *q* or every shopping list if q is missing |TRUE
| /shoppinglists | POST | Create a new shopping list|TRUE
| /shoppinglists | PUT | Update a shopping list|TRUE
| /shoppinglists | DELETE | Deletes a shopping list|TRUE
| /shoppinglists/share | POST | Shares a shopping list with another User|TRUE
| /shoppinglist_items | POST | Creates a shopping list item|TRUE
| /shoppinglist_items | PUT | Updates a shopping list item|TRUE
| /shoppinglist_items | DELETE | Deletes a shopping list item|TRUE
