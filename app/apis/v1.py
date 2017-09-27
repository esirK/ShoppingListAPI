import os

from flask import g, jsonify, Blueprint
from flask_restplus import Resource, Api, Namespace, fields, marshal
from flask_httpauth import HTTPBasicAuth

from app.apis.parsers import parser, master_parser, update_parser, shoppinglist_parser, item_parser, \
    update_shoppinglist_parser, update_shoppinglist_item_parser
from app.exceptions import InvalidToken, TokenExpired
from app.models import ShoppingList
from app.models.item import Item
from app.models.user import User

configuration = os.environ.get('CURRENT_CONFIG')

auth = HTTPBasicAuth()

bp = Blueprint('api', __name__)
api = Api(bp, version='1.0', title='ShoppingList API',
          description='A ShoppingList API For Users To Create,'
                      ' Edit and Share ShoppingLists'
          )

ns = Namespace('api', description='Endpoints for accessing '
                                  'shoppingList App Resources')
# MODELS
registration_model = ns.model('registration_args', {
    'email': fields.String(required=True, default="user@example.com"),
    'name': fields.String(required=True, default="username"),
    'password': fields.String(required=True, default="password")
})
login_model = ns.model('login_args', {
    'email': fields.String(required=True, default="user.example.com"),
    'password': fields.String(required=True, default="password")
})
update_model = ns.model('update_args', {
    'name': fields.String(required=True, default="username"),
    'password': fields.String(required=True, default="password")
})

user_model = ns.model('Model', {
    'name': fields.String(default="username"),
    'email': fields.String(default="user@example.com"),
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

item_model = ns.model('item_model', {
    'name': fields.String(default="Name"),
    'price': fields.String(default="Price"),
    'quantity': fields.String(default="Quantity"),
    'shopping_list_name': fields.String(default="ShoppingList Name "),
})
item_update_model = ns.model('item_update_model', {
    'name': fields.String(default="Item Name"),
    'new_name': fields.String(default="None"),
    'price': fields.String(default=0),
    'quantity': fields.String(default=0),
    'shopping_list_name': fields.String(default="ShoppingList Name "),
    'new_shopping_list_name': fields.String(default="None")
})


@auth.verify_password
def verify_password(email_or_token, password):
    """
    This Method is used by the HTTP-AUTH 
    extension to verify if a user is logged in using the following params
    :param email_or_token: 
    :param password: 
    :return: True or False 
    """
    # try authenticating by token
    try:
        user = User.verify_auth_token(email_or_token, configuration=configuration)
    except (InvalidToken, TokenExpired):
        # try to authenticate with email/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True


@ns.route("/register")
@ns.expect(registration_model)
class AppUsers(Resource):
    @api.response(201, "User Registered Successfully")
    @api.response(409, "User Already Exists")
    def post(self):
        args = parser.parse_args()
        email = args['email']
        username = args['name']
        password = args['password']

        if User.query.filter_by(email=email).first() is not None:
            response = jsonify({"message": email + ' Already Exists'})
            response.status_code = 409
            return response  # existing user
        user = User(email=email, username=username, password=password)
        user.save_user()
        response = jsonify({'message': user.username + " Created Successfully"})
        response.status_code = 201
        return response


@ns.route("/user")
class AppUser(Resource):
    @ns.expect(login_model)
    @api.response(401, "Unknown User or Invalid Credentials")
    def post(self):
        """
        Login a User Using email and Password
        """
        args = master_parser.parse_args()
        email = args['email']
        password = args['password']
        user = User.query.filter_by(email=email).first()
        if user:
            # User Found Check Password
            if user.check_password(password):
                g.user = user
                return marshal(user, user_model)
            else:
                response = jsonify({'message': "Wrong Credentials "})
                response.status_code = 401
                return response
        else:
            response = jsonify({'message': "No User Registered With " + email})
            response.status_code = 401
            return response

    @ns.expect(update_model)
    @auth.login_required
    @api.response(200, "User Credentials Updated Successfully")
    def put(self):
        """
        edit Account credentials
        """
        args = update_parser.parse_args()
        username = args['name']
        password = args['password']
        User.update_user(g.user, username=username, password=password)
        return marshal(g.user, user_model)


@ns.route("/shoppinglists")
class ShoppingLists(Resource):
    @api.response(201, "ShoppingList Added Successfully")
    @api.response(409, "ShoppingList Already Exist")
    @ns.expect(shopping_list_model)
    @auth.login_required
    def post(self):
        """
        Add a ShoppingList
        """
        args = shoppinglist_parser.parse_args()
        name = args['name']
        description = args['description']
        if g.user.add_shopping_list(name=name, description=description):
            response = jsonify({'message': "Shoppinglist " + name
                                           + " Created Successfully"})
            response.status_code = 201
            return response
        else:
            response = jsonify({'message': "Shoppinglist " + name
                                           + " Already Exists"})
            response.status_code = 409
            return response

    @api.response(200, "ShoppingList Updated Successfully")
    @api.response(409, "ShoppingList Does not Exist")
    @ns.expect(update_shopping_list_model)
    @auth.login_required
    def put(self):
        """
        Updates a shopping list 
        """
        args = update_shoppinglist_parser.parse_args()
        name = args['name']
        new_name = args['new_name']
        description = args['description']

        # Get shopping list
        shopping_list = ShoppingList.query.filter_by(name=name).first()
        if shopping_list is not None:
            # We got the shopping list. Now Update it
            shopping_list.update_shopping_list(new_name, description)
            response = jsonify({'message': "Shoppinglist " + name
                                           + " Updated Successfully"})
            response.status_code = 200
            return response
        else:
            response = jsonify({'message': "Shoppinglist " + name
                                           + " Does not Exists"})
            response.status_code = 409
            return response


@ns.route("/shoppinglist_items")
class Items(Resource):
    @api.response(201, "Item Added Successfully")
    @api.response(409, "Item Already Exist")
    @api.response(404, "ShoppingList Not Found")
    @ns.expect(item_update_model)
    @auth.login_required
    def post(self):
        """
        Add a ShoppingList item
        """
        args = item_parser.parse_args()
        name = args['name']
        price = args['price']
        quantity = args['quantity']
        shopping_list_name = args['shopping_list_name']
        # get shoppinglist from db
        shopping_lists = ShoppingList.query.filter_by(name=shopping_list_name).all()
        for shopping_list in shopping_lists:
            if shopping_list.owner_id == g.user.id:
                # obtain shopping list specific to this user
                if shopping_list.add_item(name=name, price=price,
                                          quantity=quantity,
                                          shoppinglist_id=shopping_list):
                    response = jsonify({'message': "Item " + name
                                                   + " Added Successfully"})
                    response.status_code = 201
                    return response
                else:
                    response = jsonify({'message': "Item " + name
                                                   + " Already exist"})
                    response.status_code = 409
                    return response
        response = jsonify({'message': "Shoppinglist " + shopping_list_name
                                       + " Not Found"})
        response.status_code = 404
        return response

    @api.response(200, "ShoppingList Item Updated Successfully")
    @api.response(404, "ShoppingList Item or Shopping List Does not Exist")
    @ns.expect(item_update_model)
    @auth.login_required
    def put(self):
        """
        Updates a shopping list Item
        """
        args = update_shoppinglist_item_parser.parse_args()
        name = args['name']
        new_name = args['new_name']
        price = args['price']
        quantity = args['quantity']
        shopping_list_name = args['shopping_list_name']
        new_shopping_list_name = args['new_shopping_list_name']

        # Get Shopping to which this item belongs to
        shopping_list = ShoppingList.query.filter_by(name=shopping_list_name) \
            .filter_by(owner_id=g.user.id).first()
        if shopping_list is not None:
            # get matching items from the shopping list

            item = Item.query.filter_by(name=name). \
                filter_by(shoppinglist_id=shopping_list.id).first()

            if item is not None:
                # Got The Item We supposed to Update
                # Check if user wants to update the items shopping list

                if new_shopping_list_name != "None":
                    # Look for the Shopping list to update to
                    new_shopping_list = ShoppingList.query. \
                        filter_by(name=new_shopping_list_name). \
                        filter_by(owner_id=g.user.id).first()

                    if new_shopping_list is not None:
                        # User has that Shopping List Now update the item
                        item.update_item(name=new_name, price=price,
                                         quantity=quantity,
                                         shoppinglist=new_shopping_list)
                    else:
                        response = jsonify({'message': "The new Shopping List " +
                                                       "'" +
                                                       new_shopping_list_name +
                                                       "'" +
                                                       " Does not Exist" + "'"})
                        response.status_code = 404
                        return response
                else:
                    item.update_item(name=new_name, price=price,
                                     quantity=quantity, shoppinglist=shopping_list)

                response = jsonify({'message': "Item " + "'" + name + "'"
                                               + " Successfully Updated"})
                response.status_code = 200
                return response
            else:

                response = jsonify({'message': "Item " + name
                                               + " Does not Exist " +
                                               "In shopping list " + "'" +
                                               shopping_list.name + "'"})
                response.status_code = 404
                return response
        else:

            response = jsonify({'message': "Shopping List " + shopping_list_name
                                           + " Does Not Exist"})
            response.status_code = 404
            return response


@ns.route("/token")
class GetAuthToken(Resource):
    decorators = [auth.login_required]

    def get(self):
        token = g.user.generate_auth_token(configurations=configuration, expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
