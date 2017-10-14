import os

from flask import g, jsonify, Blueprint, request

from flask_restplus import Resource, Api, marshal
from flask_httpauth import HTTPBasicAuth

from app.apis.parsers import parser, master_parser, update_parser, shoppinglist_parser, item_parser, \
    update_shoppinglist_parser, update_shoppinglist_item_parser, delete_shoppinglist_parser, \
    delete_shoppinglist_item_parser, paginate_query_parser, share_shoppinglist_parser
from app.apis.validators import password_validator, name_validalidatior, price_quantity_validator, numbers_validator, \
    validate_ints
from app.exceptions import InvalidToken, TokenExpired
from app.models import ShoppingList, ns, registration_model, login_model, update_model, user_model, \
    shopping_list_model, \
    update_shopping_list_model, delete_shopping_list_model, item_model, item_update_model, \
    delete_shopping_list_item_model, shopping_lists_with_items_model, share_shoppinglist_model
from app.models.item import Item
from app.models.user import User
from app.controller import save_user, add_shopping_list, add_shared_shopping_list, delete_shoppinglist, update_user, \
    update_shopping_list, share, add_item, delete_item

configuration = os.environ.get('CURRENT_CONFIG')

auth = HTTPBasicAuth()

bp = Blueprint('api', __name__)
api = Api(bp, version='1.0', title='ShoppingList API',
          description='A ShoppingList API For Users To Create,'
                      ' Edit and Share ShoppingLists'
          )


@bp.app_errorhandler(404)
def page_not_found(e):
    return jsonify({"message": "not found"}), 404


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
@ns.expect(registration_model, validate=True)
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

        invalid_name = name_validalidatior(username, "User ")

        if invalid_name:
            return invalid_name

        if password_validator(password):
            return password_validator(password)

        if User.query.filter_by(email=email).first() is not None:
            return make_json_response(409, email, " Already Exists")  # existing user

        user = User(email=email, username=username, password=password)
        save_user(user)
        return make_json_response(201, user.username, " Created Successfully")


@ns.route("/user")
class AppUser(Resource):
    @auth.login_required
    def get(self):
        """
        Get current user details
        """
        return marshal(g.user, user_model)

    @ns.expect(login_model, validate=True)
    @api.response(401, "Unknown User or Invalid Credentials")
    def post(self):
        """
        User Login
        Supply details user registered with.
        """
        args = master_parser.parse_args()
        email = args['email']
        password = args['password']
        user = User.query.filter_by(email=email).first()
        if user:
            # User Found Check Password
            if user.check_password(password):
                g.user = user
                token = g.user.generate_auth_token(configurations=configuration,
                                                   expiration=600)
                return jsonify({'token': token.decode('ascii'),
                                'duration': 600})
            else:
                return make_json_response(401, "Wrong Credentials ", " Provided")

        else:
            return make_json_response(401, "No User Registered With " + email,
                                      " Exists")

    @ns.expect(update_model, validate=True)
    @auth.login_required
    @api.response(200, "User Credentials Updated Successfully")
    def put(self):
        """
        edit Account credentials
        Only username and password can be changed.
        For Fields that the user does not intend to change, they should be left
        as 'None'
        """
        args = update_parser.parse_args()
        username = args['name']
        password = args['password']
        invalid_name = name_validalidatior(username, "Users")
        if invalid_name:
            return invalid_name

        if username == "None" and password == "None":
            return {
                "message": "No Updates Were Made"
            }
        update_user(g.user, username=username, password=password)
        response = {
            "message": "User Updated successfully",
            "User": marshal(g.user, user_model)
        }
        return response


@ns.route("/shoppinglists")
class ShoppingLists(Resource):
    @api.response(404, "ShoppingList Does not Exist")
    @auth.login_required
    @ns.expect(paginate_query_parser, validate=True)
    def get(self):
        """
        gets all shopping lists of current user if a query is not provided.
        A specific shopping list will be returned if a query is provided.
        Note that an empty list will be returned in cases where there
        is no shopping list
        """
        args = paginate_query_parser.parse_args(request)
        search_query = args.get("q")
        page = args.get('page', 1)
        limit = args.get("limit", 10)
        if search_query:
            """
            gets shopping_list(s) of current user specified by search_query
            """
            shopping_lists = ShoppingList.query. \
                filter(ShoppingList.name.like(search_query + "%")). \
                filter_by(owner_id=g.user.id).all()
            if len(shopping_lists) > 0:

                return marshal(shopping_lists, shopping_lists_with_items_model)
            else:
                return make_json_response(404, "Shopping List " + search_query,
                                          " Does Not Exist")

        shopping_lists = ShoppingList.query.filter_by(owner_id=g.user.id). \
            paginate(page, limit, True).items
        if len(shopping_lists) == 0:
            return make_json_response(200, "You Currently",
                                      "Do Not Have Any Shopping List")

        return marshal(shopping_lists, shopping_lists_with_items_model)

    @api.response(201, "ShoppingList Added Successfully")
    @api.response(409, "ShoppingList Already Exist")
    @ns.expect(shopping_list_model, validate=True)
    @auth.login_required
    def post(self):
        """
        Add a ShoppingList.
        """
        args = shoppinglist_parser.parse_args()
        name = args['name']
        description = args['description']

        invalid_name = name_validalidatior(name, "Shopping List")
        if invalid_name:
            return invalid_name

        if add_shopping_list(g.user, name=name, description=description):
            return make_json_response(201, "Shopping list " + name,
                                      " Created Successfully")
        else:
            return make_json_response(409, "Shopping list " + name,
                                      " Already Exists")

    @api.response(200, "ShoppingList Updated Successfully")
    @api.response(404, "ShoppingList Does not Exist")
    @ns.expect(update_shopping_list_model, validate=True)
    @auth.login_required
    def put(self):
        """
        Updates a shopping list 
        Both the "new_name" and "description" fields can be added
        according to which the user wants to update
        """
        args = update_shoppinglist_parser.parse_args()
        soppinglist_id = args.get('id')
        new_name = args.get('new_name')
        description = args.get('description')

        invalid_id = numbers_validator(soppinglist_id)
        if invalid_id:
            return invalid_id

        # Get shopping list
        shopping_list = ShoppingList.query.filter_by(id=soppinglist_id).first()
        if shopping_list is not None:
            # We got the shopping list. Now Update it
            if new_name or description is not None:
                update_shopping_list(shopping_list, new_name, description)
                return make_json_response(200, "Shopping list " + shopping_list.name,
                                          " Updated Successfully")
            else:
                return make_json_response(200, "Nothing was provided ", "to Updated")

        else:
            return make_json_response(404, "Shopping list " + soppinglist_id,
                                      " Does not exist")


@ns.route("/shoppinglists/<id>")
class SingleShoppingList(Resource):
    @api.response(200, "ShoppingList Found")
    @api.response(404, "ShoppingList Does not Exist")
    @auth.login_required
    def get(self, id=None):
        """
        gets the shopping list with the supplied id
        """
        if validate_ints(id):
            shopping_list = ShoppingList.query.filter_by(id=id) \
                .filter_by(owner_id=g.user.id).first()
            if shopping_list is not None:
                return marshal(shopping_list, shopping_lists_with_items_model)
            else:
                return make_json_response(404, "Shopping list with ID " + id,
                                          " Does not exist")
        else:
            return make_json_response(404, "Shopping list with ID " + id,
                                      " Does not exist. Expecting a digit id")

    @api.response(200, "ShoppingList Deleted Successfully")
    @api.response(404, "ShoppingList Does not Exist")
    @auth.login_required
    def delete(self, id=None):
        """
        Deletes a shopping list
        """

        if not validate_ints(id):
            return make_json_response(404, "Shopping list with ID " + id,
                                      " Does not exist. Expecting a digit id")

        # Get the shopping list specified and belonging to current user
        shopping_list = ShoppingList.query.filter_by(id=id) \
            .filter_by(owner_id=g.user.id).first()
        if shopping_list is not None:
            items = Item.query.filter_by(shoppinglist_id=shopping_list.id).all()
            delete_shoppinglist(shopping_list, items)
            return make_json_response(200, "Shopping list" + shopping_list.name,
                                      " Deleted Successfully")
        else:
            return make_json_response(404, "Shopping list with ID " + id,
                                      " Does not exist")


@ns.route("/shoppinglists/share")
class ShareShoppingLists(Resource):
    @api.response(200, "Shopping list shared successfully")
    @api.response(404, "Shopping list or email to share with doesn't exist")
    @ns.expect(share_shoppinglist_model, validate=True)
    @auth.login_required
    def post(self):
        """
        Shares supplied shopping list with the email provided.
        """
        args = share_shoppinglist_parser.parse_args()
        shopping_list_id = args.get('id')
        email = args.get('email')

        invalid_id = numbers_validator(shopping_list_id)
        if invalid_id:
            return invalid_id

        # Find shopping list from db
        shopping_list = ShoppingList.query.filter_by(id=shopping_list_id). \
            filter_by(owner_id=g.user.id).first()
        if shopping_list:
            # shopping list exists just share it now
            share_with = User.query.filter_by(email=email).first()
            if share_with and email != g.user.email:
                # the person exists
                if add_shared_shopping_list(shopping_list, share_with):
                    share(shopping_list, True, g.user.email)
                    return make_json_response(200, "Shopping List " +
                                              shopping_list.name,
                                              " Shared Successfully")
                else:
                    return make_json_response(200, "Shopping List With ID " +
                                              shopping_list_id,
                                              " Not Shared")
            else:
                # person don't exist or you are the person
                return make_json_response(404, "Email: " + email,
                                          " Does not exists or its your email")
        else:
            return make_json_response(404, "ShoppingList with ID " + shopping_list_id, "Does Not Exist")


@ns.route("/shoppinglist_items")
class Items(Resource):
    @api.response(201, "Item Added Successfully")
    @api.response(409, "Item Already Exist")
    @api.response(404, "ShoppingList Not Found")
    @ns.expect(item_model)
    @auth.login_required
    def post(self):
        """
        Add's a ShoppingList item
        "shopping_list_id" Is the id of the shopping_list to which the
        item will be added to.
        """
        args = item_parser.parse_args()
        name = args.get('name')
        price = args.get('price')
        quantity = args.get('quantity')
        shopping_list_id = args.get('shopping_list_id')
        # get shoppinglist from db

        invalid_name = name_validalidatior(name, "Shopping List Item")
        if invalid_name:
            return invalid_name

        invalid_price = price_quantity_validator(price, "Price")
        if invalid_price or price_quantity_validator(quantity, "Quantity"):
            return invalid_price

        invalid_id = numbers_validator(shopping_list_id)
        if invalid_id:
            return invalid_id

        shopping_list = ShoppingList.query.filter_by(id=shopping_list_id) \
            .filter_by(owner_id=g.user.id).first()
        if shopping_list:
            # Eureka!!! we found the shopping list add the item now
            if add_item(shopping_list, name=name, price=price,
                        quantity=quantity, owner_id=g.user.id):
                return make_json_response(201, "Item " + name, " Added Successfully")

            else:
                return make_json_response(409, "Item " + name, " Already exist")

        return make_json_response(404, "Shoppinglist with ID " + str(shopping_list_id),
                                  " Not Found")

    @api.response(200, "ShoppingList Item Updated Successfully")
    @api.response(404, "ShoppingList Item or Shopping List Does not Exist")
    @ns.expect(item_update_model)
    @auth.login_required
    def put(self):
        """
        Updates a shopping list Item
        For Fields that the user does not want to update they can be omitted
        """
        args = update_shoppinglist_item_parser.parse_args()
        item_id = args.get('id')
        new_name = args.get('new_name')
        price = args.get('price')
        quantity = args.get('quantity')
        new_shopping_list_id = args.get('new_shopping_list_id')

        item = Item.query.filter_by(id=item_id).first()

        if item is not None and new_shopping_list_id is None:
            # Got The Item We supposed to Update
            item.update_item(name=new_name, price=price,
                             quantity=quantity)
            return make_json_response(200, "Item " + "'" + item.name + "'",
                                      " Successfully Updated")

        if item is None:
            return make_json_response(404, "Item with id " + str(item_id),
                                      "Does not Exist '" +
                                      "'")

        # Check if user wants to update the items shopping list
        if new_shopping_list_id is not None:
            # Look for the Shopping list to update to
            new_shopping_list = ShoppingList.query. \
                filter_by(id=new_shopping_list_id).first()

            if new_shopping_list is not None:
                # User has that Shopping List Now update the item
                item.update_item(name=new_name, price=price,
                                 quantity=quantity,
                                 shoppinglist=new_shopping_list)
            else:
                return make_json_response(404, "The new Shopping List with ID " +
                                          "'" +
                                          str(new_shopping_list_id) +
                                          "'",
                                          " Does not Exist")


@ns.route("/shoppinglist_items/<id>")
class SingleItem(Resource):
    @api.response(200, "Item Found")
    @api.response(404, "Item Does Not Exist")
    @auth.login_required
    def get(self, id=None):
        """
        Returns a single Item with the supplied id
        """
        if validate_ints(id):
            item = Item.query.filter_by(id=id) \
                .filter_by(owner_id=g.user.id).first()
            if item is not None:
                return marshal(item, item_model)
            else:
                return make_json_response(404, "Item with ID " + id,
                                          " Does not exist")
        else:
            return make_json_response(404, "Item with ID " + id,
                                      " Does not exist. Expecting a digit id")

    @api.response(200, "ShoppingList Item Deleted Successfully")
    @api.response(404, "ShoppingList Item Does not Exist")
    @auth.login_required
    def delete(self, id=None):
        """
        Deletes a shopping list Item
        """
        if not validate_ints(id):
            return make_json_response(404, "Shopping list with ID " + id,
                                      " Does not exist. Expecting a digit id")
        # Check if That Item exist
        item = Item.query.filter_by(id=id).filter_by(owner_id=g.user.id).first()
        if item:
            delete_item(item)
            return make_json_response(200, "Item " + item.name,
                                      " Deleted Successfully")
        else:
            return make_json_response(404, "Item With id " + str(id),
                                      " Does Not Exist.")


def make_json_response(status_code, name_obj, message):
    response = jsonify({'message': name_obj + " " + message})
    response.status_code = status_code
    return response


@ns.route("/token")
class GetAuthToken(Resource):
    decorators = [auth.login_required]

    def get(self):
        """
        Generate authentication token for logged in user
        Use the generated Authentication Token for other
         requests for security reasons
        """
        token = g.user.generate_auth_token(configurations=configuration,
                                           expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
