from datetime import datetime

import sqlalchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import make_transient
from werkzeug.security import generate_password_hash, check_password_hash

from app import config
from app.init_db import db
from app.exceptions import UserAlreadyExist
from app.models.shoppinglist import ShoppingList


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(104))
    shopping_lists = db.relationship(ShoppingList, backref='owner', lazy='dynamic')
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
        return s.dumps({'id': self.id})

    def save_user(self):
        """
        Adds current user into the Database
        """
        try:
            db.session.add(self)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise UserAlreadyExist
        return True

    def update_user(self, username, password):
        """
        Updates A user Data. For account management
        """
        if password != "None":
            self.set_password(password)
        if username != "None":
            self.username = username
        db.session.commit()

    def add_shopping_list(self, name, description):
        """
        Adds a ShoppingList to this user account
        """
        shopping_lst = ShoppingList.query.filter_by(name=name)\
            .filter_by(owner_id=self.id).first()
        if shopping_lst:
            # user has the shopping list
            return False

        shopping_list = ShoppingList(name=name, description=description,
                                     owner=self)

        db.session.add(shopping_list)
        db.session.commit()
        return True

    def add_shared_shopping_list(self, shopping_list, share_with):
        # check if shopping list exist
        shopping_lst = ShoppingList.query.filter_by(name=shopping_list.name)\
            .filter_by(owner_id=share_with.id).first()

        if shopping_lst:
            # user has the shopping list already
            return False
        else:
            db.session.expunge(shopping_list)
            make_transient(shopping_list)
            shopping_list.id = None
            shopping_list.owner_id = share_with.id
            db.session.add(shopping_list)
            db.session.flush()
            db.session.commit()
            return True

    def delete_shoppinglist(self, shoppinglist, items):
        db.session.delete(shoppinglist)
        for item in items:
            db.session.delete(item)

        db.session.commit()

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
