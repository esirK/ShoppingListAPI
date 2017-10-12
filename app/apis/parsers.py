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
                                 help='Shoppinglist name Not Provided')

shoppinglist_parser.add_argument('description', type=str, required=True,
                                 help='Shoppinglist description Not Provided')

update_shoppinglist_parser = reqparse.RequestParser()
update_shoppinglist_parser.add_argument('id', type=str, required=True,
                                        help='Shoppinglist Not Provided')
update_shoppinglist_parser.add_argument('new_name', type=str,
                                        help='New Shoppinglist Name')
shoppinglist_parser.add_argument('description', type=str,
                                 help='Shoppinglist description')

share_shoppinglist_parser = reqparse.RequestParser()
share_shoppinglist_parser.add_argument('id', type=str, required=True,
                                       help='Shoppinglist id Not Provided')
share_shoppinglist_parser.add_argument('email', type=inputs.email(), required=True,
                                       help='Email to share with')

delete_shoppinglist_parser = reqparse.RequestParser()
delete_shoppinglist_parser.add_argument('id', type=str, required=True,
                                        help='Shoppinglist ID required')

item_parser = reqparse.RequestParser()
item_parser.add_argument('name', type=str, required=True,
                         help='Item Name')

item_parser.add_argument('price', type=int, required=True,
                         help='Item Price has to be an Number')
item_parser.add_argument('quantity', type=int, required=True,
                         help='Item Quantity has to be an Number')
item_parser.add_argument('shopping_list_id', type=int, required=True,
                         help='Shoppinglist(id) to add item to Required')

delete_shoppinglist_item_parser = reqparse.RequestParser()
delete_shoppinglist_item_parser.add_argument('id', type=int, required=True,
                                             help='ID of Shoppinglist Item to delete Required')


update_shoppinglist_item_parser = reqparse.RequestParser()
update_shoppinglist_item_parser.add_argument('price', type=int, required=True,
                                             help='Item Price has to be an Number')
update_shoppinglist_item_parser.add_argument('quantity', type=int, required=True,
                                             help='Item Quantity has to be an Number')

update_shoppinglist_item_parser.add_argument('id', type=str, required=True,
                                             help='Item Id required')
update_shoppinglist_item_parser.add_argument('new_name', type=str,
                                             help='New Item Name')
update_shoppinglist_item_parser.add_argument('new_shopping_list_id', type=int,
                                             help='New shopping list ID required')

paginate_query_parser = reqparse.RequestParser()
paginate_query_parser.add_argument(
    'q', type=str, required=False, help="Search for"
)
paginate_query_parser.add_argument(
    'page', type=int, required=False, help="page of results"
)
paginate_query_parser.add_argument(
    'limit', type=int, required=False, help="limit per page"
)
