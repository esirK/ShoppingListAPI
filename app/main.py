import os

from flask import g, jsonify, request, url_for, Blueprint
from werkzeug.exceptions import abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash

from app import db
from app.exceptions import InvalidToken, TokenExpired
from app.models import ShoppingList
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
    username = result.get('username', " ")
    password = result.get('password', " ")
    email = result.get('email', " ")
    if email.isspace() or len(email) == 0 or password.isspace() \
            or len(password) == 0 or username.isspace() or len(username) == 0:
        abort(400)  # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({email: 'Already Exists'})  # existing user
    user = User(email=email, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201, \
           {'Location': url_for('api.add_user', id=user.id, _external=True)}


@api.route('/login', methods=['POST'])
def login():
    """
    A route to allow a user to login to the shoppinglist app
    """
    result = request.get_json()
    email = result['email']
    password = result['password']

    if email.isspace() or len(email) == 0 or \
            password.isspace() or len(password) == 0:
        abort(400)  # missing arguments
    user = User.query.filter_by(email=email).first()
    if user:
        if user.check_password(password):
            g.user = user
            return jsonify({user.username: 'Loggedin'})
        else:
            return jsonify({"Invalid": 'Invalid Password'})
    else:
        return jsonify({"User": 'Does Not Exists'})


@api.route('/update_account', methods=['POST', 'GET'])
@auth.login_required
def update_account():
    """
    User Can change their username, email or password here
    """
    result = request.get_json()
    username = result.get('username', " ")
    password = result.get('password', " ")
    email = result.get('email', " ")
    if email.isspace() or len(email) == 0 or password.isspace()\
            or len(password) == 0 or username.isspace() or len(username) == 0:
        abort(400)  # missing arguments
    user = User.query.filter_by(email=g.user.email).first()
    user.email = email
    user.username = username
    user.password = generate_password_hash(password)
    db.session.commit()
    return jsonify({"Update": "Details Updated Successfully"})


@api.route('/create_shopping_list', methods=['POST'])
@auth.login_required
def create_shopping_list():
    """ 
    This Method adds a shopping_list into current user's shopping lists
    """
    result = request.get_json()
    name = result.get('name')
    description = result.get('description')
    if name.isspace() or len(name) == 0 or description.isspace()\
            or len(description) == 0:
            abort(400)  # missing arguments

    shopping_lists = ShoppingList.query.filter_by(name=name).all()

    for shopping_lst in shopping_lists:
        if shopping_lst.owner_id == g.user.id:
            return jsonify({shopping_lst.name: "ShoppingList Already Exists"})
    shoppingList = ShoppingList(name=name, description=description,
                                owner=g.user)
    db.session.add(shoppingList)
    db.session.commit()
    return jsonify({shoppingList.name: "ShoppingList Added Successfully"})


@api.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(configurations=configuration,
                                       expiration=600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
