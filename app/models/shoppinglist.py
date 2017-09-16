from app import db


class ShoppingList(db.Model):
    __tablename__ = "shoppinglists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(180))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner_id = owner.id
