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
    'name': fields.String(required=True, default="None"),
    'password': fields.String(required=True, default="None")
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

shopping_list_display_model = shopping_list_model.clone(
    'shopping_list_display_model', {
        'shared': fields.String(default="False"),
        'shared_by': fields.String(default="nobody")
    })
update_shopping_list_model = ns.model('update_shopping_list_model', {
    'description': fields.String(default="None"),
    'new_name': fields.String(default="New name"),
})
delete_shopping_list_model = ns.model('delete_shopping_list_model', {
    'id': fields.String(default="id")
})
share_shoppinglist_model = ns.model('share_shoppinglist_model', {
    'id': fields.String(default="id"),
    'email': fields.String(default="sharewith@example.com"),
})
item_model = ns.model('item_model', {
    'name': fields.String(default="Name"),
    'price': fields.String(default="Price"),
    'quantity': fields.String(default="Quantity"),
    'shoppinglist_id': fields.String(default="id"),
})
result_item_model = ns.model('result_item_model', {
    'name': fields.String(default="Name"),
    'price': fields.String(default="Price"),
    'quantity': fields.String(default="Quantity"),
    'id': fields.String(default="0")
})
shopping_lists_with_items_model = shopping_list_display_model. \
    clone('shopping_lists_with_items_model',
          {
              'items': fields.List(fields.Nested(result_item_model)),
              'id': fields.String(default="id")

          })

item_update_model = ns.model('item_update_model', {
    'id': fields.String(default="Item id"),
    'new_name': fields.String(default="None"),
    'price': fields.String(default=0),
    'quantity': fields.String(default=0),
    'new_shopping_list_id': fields.String(default="0")
})
delete_shopping_list_item_model = ns.model('delete_shopping_list_item_model', {
    'id': fields.String(default="0")
})
