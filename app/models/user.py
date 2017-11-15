from datetime import datetime

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash

from app import config
from app.init_db import db
from app.models.item import Item
from app.models.shoppinglist import ShoppingList


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(104))
    shopping_lists = db.relationship(ShoppingList, backref='owner', lazy='dynamic')
    items = db.relationship(Item, backref='items_owner', lazy='dynamic')
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def __repr__(self):
        """
         string representation that can be used for debugging
         and testing purposes. 
        """
        return '<User %r>' % self.email

    def set_password(self, password):
        """
        Sets current users password as a password hash
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expiration=600, configurations=""):
        s = Serializer(config[configurations].SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id, 'username': self.username})

    @staticmethod
    def verify_auth_token(token, configuration):
        s = Serializer(config[configuration].SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            from app.exceptions import TokenExpired
            raise TokenExpired  # valid token, but expired
        except BadSignature:
            from app.exceptions import InvalidToken
            raise InvalidToken  # invalid token
        user = User.query.get(data['id'])
        return user
