from werkzeug.security import generate_password_hash

from app import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.shopping_lists = {}

    def __repr__(self):
        """
         string representation that can be used for debugging
         and testing purposes. 
        """
        return '<User %r>' % self.email
