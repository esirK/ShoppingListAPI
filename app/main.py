import os

from flask import g, jsonify, request, url_for, Blueprint
from werkzeug.exceptions import abort
from flask_httpauth import HTTPBasicAuth

from app import db
from app.exceptions import InvalidToken, TokenExpired
from app.models.user import User

auth = HTTPBasicAuth()

api = Blueprint('api', __name__)
configuration = os.environ.get('CURRENT_CONFIG')


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


@api.route('/register', methods=['POST'])
def add_user():
    """Route for creating a new User"""
    result = request.get_json()
    username = result['username']
    password = result['password']
    email = result['email']
    if email is None or password is None or username is None:
        abort(400)  # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({email: 'Already Exists'})  # existing user
    user = User(email=email, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201, \
           {'Location': url_for('api.add_user', id=user.id, _external=True)}


@api.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(configurations=configuration, expiration=600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
