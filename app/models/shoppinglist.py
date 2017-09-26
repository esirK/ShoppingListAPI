from datetime import datetime

from app import db
from app.models.item import Item


class ShoppingList(db.Model):
    __tablename__ = "shoppinglists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(180))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship(Item, backref='container', lazy='dynamic')
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner_id = owner.id

    def update_shopping_list(self, name, description):
        """
        Updates Shopping List Data
        """
        if description == "None":
            self.name = name
        else:
            self.name = name
            self.description = description
        db.session.commit()

    def add_item(self, name, price, quantity, shoppinglist_id):
        """
        Adds an item to the current shoppinglist
        """
        item = Item(name=name, price=price, quantity=quantity,
                    shoppinglist=shoppinglist_id)
        if self.check_item(name):
            db.session.add(item)
            db.session.commit()
            return True
        else:
            return False

    def check_item(self, item_name):
        """
        Checks if an item exists in this shopping list before adding it
        :return: 
        """
        items = Item.query.filter_by(name=item_name).all()
        for item in items:
            if item.shoppinglist_id == self.id:  # Item already exist
                return False
        return True
