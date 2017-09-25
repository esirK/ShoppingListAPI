import os

from flask import g, jsonify, Blueprint
from flask_restplus import Resource, reqparse, inputs, Api, Namespace, fields, marshal
from flask_httpauth import HTTPBasicAuth

from app.exceptions import InvalidToken, TokenExpired
from app.models.user import User

auth = HTTPBasicAuth()

configuration = os.environ.get('CURRENT_CONFIG')

bp = Blueprint('api', __name__)
api = Api(bp, version='1.0', title='ShoppingList API',
          description='A ShoppingList API For Users To Create,'
                      ' Edit and Share ShoppingLists'
          )

ns = Namespace('api', description='Endpoints for accessing '
                                  'shoppingList App Resources')

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
        A Logged in user can edit his/her credentials
        """
        args = update_parser.parse_args()
        username = args['name']
        password = args['password']
        User.update_user(g.user, username=username, password=password)
        return marshal(g.user, user_model)


@ns.route("/token")
class GetAuthToken(Resource):
    decorators = [auth.login_required]

    def get(self):
        token = g.user.generate_auth_token(configurations=configuration, expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
