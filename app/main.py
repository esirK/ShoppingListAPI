import os

from flask import g, jsonify
from flask_restplus import Resource, reqparse
from flask_httpauth import HTTPBasicAuth

from app import db, api
from app.exceptions import InvalidToken, TokenExpired
from app.models.user import User

auth = HTTPBasicAuth()

configuration = os.environ.get('CURRENT_CONFIG')

ns = api.namespace('api', description='ShoppingList Endpoints')


@auth.verify_password
def verify_password(email_or_token, password):
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
                    help='Username Of User Being Registered', location='form')
parser.add_argument('email', type=str, required=True,
                    help='Email Of User Being Registered', location='form')
parser.add_argument('password', type=str, required=True,
                    help='Password Of User Being Registered', location='form')


@ns.route('/register')
class AddUser(Resource):
    @api.doc(parser=parser)
    def post(self):
        args = parser.parse_args()
        email = args['email']
        username = args['name']
        password = args['password']

        if User.query.filter_by(email=email).first() is not None:
            return jsonify({"message": email+' Already Exists'})  # existing user
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': user.username + " Created Successfully"})


@auth.login_required
class GetAuthToken(Resource):
    def get(self):
        token = g.user.generate_auth_token(configurations=configuration, expiration=600)
        return jsonify({'token': token.decode('ascii'), 'duration': 600})