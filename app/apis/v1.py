import os

from flask import g, jsonify, Blueprint
from flask_restplus import Resource, Api, Namespace, fields, marshal
from flask_httpauth import HTTPBasicAuth

from app.apis.parsers import parser, master_parser, update_parser, shoppinglist_parser, item_parser, \
    update_shoppinglist_parser, update_shoppinglist_item_parser, delete_shoppinglist_parser
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
delete_shopping_list_model = ns.model('delete_shopping_list_model', {
    'name': fields.String(default="Shopping List name")
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
        """
        Registers a new User into the App
        """
        args = parser.parse_args()
        email = args['email']
        username = args['name']
        password = args['password']

        if User.query.filter_by(email=email).first() is not None:
            return make_response(409, email, " Already Exists")  # existing user

        user = User(email=email, username=username, password=password)
        user.save_user()
        return make_response(201, user.username, " Created Successfully")


@ns.route("/user")
class AppUser(Resource):
    @ns.expect(login_model)
    @api.response(401, "Unknown User or Invalid Credentials")
    def post(self):
        """
        User Login
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
                return make_response(401, "Wrong Credentials ", " Provided")

        else:
            return make_response(401, "No User Registered With " + email, " Exists")

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
            return make_response(201, "Shopping list " + name,
                                 " Created Successfully")
        else:
            return make_response(409, "Shopping list " + name, " Already Exists")

    @api.response(200, "ShoppingList Updated Successfully")
    @api.response(404, "ShoppingList Does not Exist")
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
            return make_response(200, "Shopping list " + name, " Updated Successfully")

        else:
            return make_response(404, "Shopping list " + name, " Does not exist")

    @api.response(200, "ShoppingList Deleted Successfully")
    @api.response(404, "ShoppingList Does not Exist")
    @ns.expect(delete_shopping_list_model)
    @auth.login_required
    def delete(self):
        """
        Deletes a shopping list 
        """
        args = delete_shoppinglist_parser.parse_args()
        name = args['name']
        # Get the shopping list specified and belonging to current user
        shopping_list = ShoppingList.query.filter_by(name=name) \
            .filter_by(owner_id=g.user.id).first()
        if shopping_list is not None:
            g.user.delete_shoppinglist(shopping_list)
            return make_response(200, "Shopping list " + name, " Deleted Successfully")
        else:
            return make_response(404, "Shopping list " + name, " Does not exist")


@ns.route("/shoppinglist_items")
class Items(Resource):
    @api.response(201, "Item Added Successfully")
    @api.response(409, "Item Already Exist")
    @api.response(404, "ShoppingList Not Found")
    @ns.expect(item_update_model)
    @auth.login_required
    def post(self):
        """
        Add's a ShoppingList item
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
                    return make_response(201, "Item " + name, " Added Successfully")

                else:
                    return make_response(409, "Item " + name, " Already exist")

        return make_response(404, "Shoppinglist " + shopping_list_name,
                             " Not Found")

    @api.response(200, "ShoppingList Item Updated Successfully")
    @api.response(404, "ShoppingList Item or Shopping List Does not Exist")
    @ns.expect(item_update_model)
    @auth.login_required
    def put(self):
        """
        Updates a shopping list Item
        For Fields that the user does not want to update leave them as they are on the model
        i.e "None' for "new_name" and "new_shopping_list_name" and '0' for "price" and "quantity"
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

                        return make_response(404, "The new Shopping List " +
                                             "'" +
                                             new_shopping_list_name +
                                             "'",
                                             " Does not Exist")

                else:
                    item.update_item(name=new_name, price=price,
                                     quantity=quantity, shoppinglist=shopping_list)

                return make_response(200, "Item " + "'" + name + "'",
                                     " Successfully Updated")

            else:
                return make_response(404, "Item " + name,
                                     "Does not Exist In shopping list '" + shopping_list.name + "'")
        else:
            return make_response(404, "Shopping List " + shopping_list_name, "Does Not Exist")


def make_response(status_code, name_obj, message):
    response = jsonify({'message': name_obj + " " + message})
    response.status_code = status_code
    return response


@ns.route("/token")
class GetAuthToken(Resource):
    decorators = [auth.login_required]

    def get(self):
        """
        Generate authentication token for logged in user
        Use the generated Authentication Token for other requests for security reasons
        """
        token = g.user.generate_auth_token(configurations=configuration, expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
