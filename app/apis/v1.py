import os

from flask import g, jsonify, Blueprint, request

from flask_restplus import Resource, Api, marshal
from flask_httpauth import HTTPBasicAuth

from app.apis.parsers import parser, master_parser, update_parser, shoppinglist_parser, item_parser, \
    update_shoppinglist_parser, update_shoppinglist_item_parser, delete_shoppinglist_parser, \
    delete_shoppinglist_item_parser, paginate_query_parser, share_shoppinglist_parser
from app.exceptions import InvalidToken, TokenExpired
from app.models import ShoppingList, ns, registration_model, login_model, update_model, user_model, \
    shopping_list_model, \
    update_shopping_list_model, delete_shopping_list_model, item_model, item_update_model, \
    delete_shopping_list_item_model, shopping_lists_with_items_model, share_shoppinglist_model
from app.models.item import Item
from app.models.user import User

configuration = os.environ.get('CURRENT_CONFIG')

auth = HTTPBasicAuth()

bp = Blueprint('api', __name__)
api = Api(bp, version='1.0', title='ShoppingList API',
          description='A ShoppingList API For Users To Create,'
                      ' Edit and Share ShoppingLists'
          )


@bp.app_errorhandler(404)
def page_not_found():
    return jsonify({"message": "not found"})


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
    @auth.login_required
    def get(self):
        """
        Get current user details
        """
        return marshal(g.user, user_model)

    @ns.expect(login_model)
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
                return make_response(401, "Wrong Credentials ", " Provided")

        else:
            return make_response(401, "No User Registered With " + email,
                                 " Exists")

    @ns.expect(update_model)
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
        User.update_user(g.user, username=username, password=password)
        return marshal(g.user, user_model)


@ns.route("/shoppinglists")
class ShoppingLists(Resource):
    @api.response(404, "ShoppingList Does not Exist")
    @auth.login_required
    @ns.expect(paginate_query_parser)
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
            gets shopping_list of current user specified by search_query
            """
            shopping_list = ShoppingList.query. \
                filter_by(owner_id=g.user.id).filter_by(name=search_query).first()
            if shopping_list:
                return marshal(shopping_list, shopping_lists_with_items_model)
            else:
                return make_response(404, "Shopping List " + search_query,
                                     " Does Not Exist")
        else:
            shopping_lists = ShoppingList.query.filter_by(owner_id=g.user.id).\
                paginate(page, limit, True).items
            return marshal(shopping_lists, shopping_lists_with_items_model)

    @api.response(201, "ShoppingList Added Successfully")
    @api.response(409, "ShoppingList Already Exist")
    @ns.expect(shopping_list_model)
    @auth.login_required
    def post(self):
        """
        Add a ShoppingList.
        """
        args = shoppinglist_parser.parse_args()
        name = args['name']
        description = args['description']
        if g.user.add_shopping_list(name=name, description=description):
            return make_response(201, "Shopping list " + name,
                                 " Created Successfully")
        else:
            return make_response(409, "Shopping list " + name,
                                 " Already Exists")

    @api.response(200, "ShoppingList Updated Successfully")
    @api.response(404, "ShoppingList Does not Exist")
    @ns.expect(update_shopping_list_model)
    @auth.login_required
    def put(self):
        """
        Updates a shopping list 
        Both the "new_name" and "description" fields can be left as 'None'
        if the user does not intend to update either
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
            return make_response(200, "Shopping list " + name,
                                 " Updated Successfully")

        else:
            return make_response(404, "Shopping list " + name,
                                 " Does not exist")

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
            return make_response(200, "Shopping list " + name,
                                 " Deleted Successfully")
        else:
            return make_response(404, "Shopping list " + name,
                                 " Does not exist")


@ns.route("/shoppinglists/share")
class ShareShoppingLists(Resource):
    @api.response(200, "Shopping list shared successfully")
    @api.response(404, "Shopping list or email to share with doesn't exist")
    @ns.expect(share_shoppinglist_model)
    @auth.login_required
    def post(self):
        """
        Shares supplied shopping list with the email provided.
        """
        args = share_shoppinglist_parser.parse_args()
        name = args['name']
        email = args['email']

        # Find shopping list from db
        shopping_list = ShoppingList.query.filter_by(name=name).\
            filter_by(owner_id=g.user.id).first()
        if shopping_list:
            # shopping list exists just share it now
            share_with = User.query.filter_by(email=email).first()
            if share_with and email != g.user.email:
                # the person exists
                if g.user.add_shared_shopping_list(shopping_list, share_with):
                    shopping_list.share(True, g.user.email)
                    return make_response(200, "Shopping List "+name,
                                         " Shared Successfully")
                else:
                    return make_response(200, "Shopping List " + name,
                                         " Not Shared")
            else:
                # person don't exist or you are the person
                return make_response(404, "Email: "+email,
                                     " Does not exists or its your email")
        else:
            return make_response(404, "ShoppingList "+name, "Does Not Exist")


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
        "shopping_list_name" Is the name of the shopping_list to which the 
        item will be added to.
        """
        args = item_parser.parse_args()
        name = args['name']
        price = args['price']
        quantity = args['quantity']
        shopping_list_name = args['shopping_list_name']
        # get shoppinglist from db

        shopping_list = ShoppingList.query.filter_by(name=shopping_list_name) \
            .filter_by(owner_id=g.user.id).first()
        if shopping_list:
            # Eureka!!! we found the shopping list add the item now
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
        For Fields that the user does not want to update leave
        them as they are on the model
        i.e "None' for "new_name" and "new_shopping_list_name" and '0'
         for "price" and "quantity"
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
                                     quantity=quantity,
                                     shoppinglist=shopping_list)

                return make_response(200, "Item " + "'" + name + "'",
                                     " Successfully Updated")

            else:
                return make_response(404, "Item " + name,
                                     "Does not Exist In shopping list '" +
                                     shopping_list.name + "'")
        else:
            return make_response(404, "Shopping List " + shopping_list_name,
                                 "Does Not Exist")

    @api.response(200, "ShoppingList Item Deleted Successfully")
    @api.response(404, "ShoppingList or ShoppingList Item Does not Exist")
    @ns.expect(delete_shopping_list_item_model)
    @auth.login_required
    def delete(self):
        """
        Deletes a shopping list Item
        """
        args = delete_shoppinglist_item_parser.parse_args()
        name = args['name']
        shopping_list_name = args['shopping_list_name']

        # Check if That shopping list exist
        shopping_list = ShoppingList.query. \
            filter_by(name=shopping_list_name). \
            filter_by(owner_id=g.user.id).first()
        if shopping_list:
            # Check if That Item Now Exists
            item = Item.query.filter_by(name=name). \
                filter_by(shoppinglist_id=shopping_list.id).first()
            if item:
                shopping_list.delete_item(item)
                return make_response(200, "Item " + name,
                                     " Deleted Successfully")
            else:
                return make_response(404, "Item " + name,
                                     " Does Not Exist.")
        else:
            return make_response(404, "ShoppingList " + shopping_list_name,
                                 "Does not Exist.")


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
        Use the generated Authentication Token for other
         requests for security reasons
        """
        token = g.user.generate_auth_token(configurations=configuration,
                                           expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
