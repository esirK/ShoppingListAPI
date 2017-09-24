import os

from flask import g, jsonify, Blueprint
from flask_restplus import Resource, reqparse, inputs, Api, Namespace
from flask_httpauth import HTTPBasicAuth

from app import db
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


parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True,
                    help='Username Of User Being Registered')
parser.add_argument('email', type=inputs.email(), required=True,
                    help='Email Of User Being Registered')
parser.add_argument('password', type=str, required=True,
                    help='Password Of User Being Registered')


@ns.route("/register")
class AppUsers(Resource):
    @api.doc(parser=parser)
    @api.expect(parser)
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
        db.session.add(user)
        db.session.commit()
        response = jsonify({'message': user.username + " Created Successfully"})
        response.status_code = 201
        return response


@ns.route("/token")
class GetAuthToken(Resource):
    decorators = [auth.login_required]

    def get(self):
        token = g.user.generate_auth_token(configurations=configuration, expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})
