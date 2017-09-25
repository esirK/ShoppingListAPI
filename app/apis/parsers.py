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

item_parser = reqparse.RequestParser()
item_parser.add_argument('name', type=str, required=True,
                         help='Item Name')

item_parser.add_argument('price', type=int, required=True,
                         help='Item Price')
item_parser.add_argument('quantity', type=int, required=True,
                         help='Item Quantity')
item_parser.add_argument('shopping_list_name', type=str, required=True,
                         help='Shoppinglist(Name) to add item to')
