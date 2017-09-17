import os

from flask import g, jsonify, request, url_for
from werkzeug.exceptions import abort
from flask_httpauth import HTTPBasicAuth

from app import create_app, db
from app.models.user import User

auth = HTTPBasicAuth()
app = create_app(os.environ.get('CURRENT_CONFIG'))


@auth.verify_password
def verify_password(email_or_token, password):
    # try authenticating by token
    user = User.verify_auth_token(email_or_token, configuration=os.environ.get('CURRENT_CONFIG'))
    if not user:
        # try to authenticate with email/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True


@app.route('/api/1_0/register', methods=['POST'])
def add_user():
    """Route for creating a new User"""
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if email is None or password is None or username is None:
        abort(400)  # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        abort(400)  # existing user
    user = User(email=email, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}), 201, \
           {'Location': url_for('add_user', id=user.id, _external=True)}


@app.route('/api/1_0/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
