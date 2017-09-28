from flask_restplus import reqparse, inputs

master_parser = reqparse.RequestParser()
master_parser.add_argument('email', type=inputs.email(), required=True,
                           help='Email Of User Being Registered')
master_parser.add_argument('password', type=str, required=True,
                           help='Password Of User Being Registered')

parser = master_parser.copy()
parser.add_argument('name', type=str, required=True,
                    help='Username Of User Being Registered')

update_parser = reqparse.RequestParser()
update_parser.add_argument('name', type=str, required=True,
                           help='Username')
update_parser.add_argument('password', type=str, required=True,
                           help='Password')

shoppinglist_parser = reqparse.RequestParser()
shoppinglist_parser.add_argument('name', type=str, required=True,
                                 help='Shoppinglist Name')

shoppinglist_parser.add_argument('description', type=str, required=True,
                                 help='Shoppinglist description')

update_shoppinglist_parser = shoppinglist_parser.copy()
update_shoppinglist_parser.add_argument('new_name', type=str, required=True,
                                        help='New Shoppinglist Name')

delete_shoppinglist_parser = reqparse.RequestParser()
delete_shoppinglist_parser.add_argument('name', type=str, required=True,
                                        help='Name of Shoppinglist to delete')

item_parser = reqparse.RequestParser()
item_parser.add_argument('name', type=str, required=True,
                         help='Item Name')

item_parser.add_argument('price', type=int, required=True,
                         help='Item Price')
item_parser.add_argument('quantity', type=int, required=True,
                         help='Item Quantity')
item_parser.add_argument('shopping_list_name', type=str, required=True,
                         help='Shoppinglist(Name) to add item to')

update_shoppinglist_item_parser = item_parser.copy()
update_shoppinglist_item_parser.add_argument('new_name', type=str, required=True,
                                             help='New Item Name')
update_shoppinglist_item_parser.add_argument('new_shopping_list_name', type=str, required=True,
                                             help='New shopping list Name')
