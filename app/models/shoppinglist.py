from datetime import datetime

from app.init_db import db
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
        check_item = Item.query.filter_by(name=name).filter_by(shoppinglist_id=self.id).first()
        if not check_item:
            db.session.add(item)
            db.session.commit()
            return True
        else:
            return False

    def delete_item(self, item):
        """
        Deletes an item from this shopping list
        :param item: 
        """
        db.session.delete(item)
        db.session.commit()
