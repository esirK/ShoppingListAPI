from flask_restplus import fields, Namespace

from . import item
from . import shoppinglist
from . import user

Item = item.Item
User = user.User
ShoppingList = shoppinglist.ShoppingList

ns = Namespace('api', description='Endpoints for accessing '
                                  'shoppingList App Resources')
# MODELS
registration_model = ns.model('registration_args', {
    'email': fields.String(required=True, default="user@example.com"),
    'name': fields.String(required=True, default="username"),
    'password': fields.String(required=True, default="password")
})
login_model = ns.model('login_args', {
    'email': fields.String(required=True, default="user@example.com"),
    'password': fields.String(required=True, default="password")
})
update_model = ns.model('update_args', {
    'name': fields.String(required=True, default="username"),
    'password': fields.String(required=True, default="password")
})

user_model = ns.model('Model', {
    'username': fields.String(default="username"),
    'email': fields.String(default="user@example.com"),
    'joined_on': fields.DateTime,
    'date_modified': fields.DateTime
})

shopping_list_model = ns.model('shopping_list_model', {
    'name': fields.String(default="Name"),
    'description': fields.String(default="Short description..."),
})

update_shopping_list_model = ns.model('update_shopping_list_model', {
    'name': fields.String(default="Shopping List name"),
    'new_name': fields.String(default="New name"),
    'description': fields.String(default="None"),
})
delete_shopping_list_model = ns.model('delete_shopping_list_model', {
    'name': fields.String(default="Shopping List name")
})
share_shoppinglist_model = ns.model('share_shoppinglist_model', {
    'name': fields.String(default="Shopping list name"),
    'email': fields.String(default="sharewith@example.com"),
})
item_model = ns.model('item_model', {
    'name': fields.String(default="Name"),
    'price': fields.String(default="Price"),
    'quantity': fields.String(default="Quantity"),
    'shopping_list_name': fields.String(default="ShoppingList Name "),
})
result_item_model = ns.model('result_item_model', {
    'name': fields.String(default="Name"),
    'price': fields.String(default="Price"),
    'quantity': fields.String(default="Quantity"),
})
shopping_lists_with_items_model = shopping_list_model. \
    clone('shopping_lists_with_items_model',
          {
              'items': fields.List(fields.Nested(result_item_model))
          })

item_update_model = ns.model('item_update_model', {
    'name': fields.String(default="Item Name"),
    'new_name': fields.String(default="None"),
    'price': fields.String(default=0),
    'quantity': fields.String(default=0),
    'shopping_list_name': fields.String(default="ShoppingList Name "),
    'new_shopping_list_name': fields.String(default="None")
})
delete_shopping_list_item_model = ns.model('delete_shopping_list_item_model', {
    'name': fields.String(default="ShoppingList Item name"),
    'shopping_list_name': fields.String(default="ShoppingList the Item belongs to.")
})
