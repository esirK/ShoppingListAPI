from datetime import datetime

from app.init_db import db


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    price = db.Column(db.Integer())
    quantity = db.Column(db.Integer())
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglists.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    modified_on = db.Column(db.DateTime(), default=datetime.utcnow,
                            onupdate=datetime.utcnow)

    def __init__(self, name, price, quantity, shoppinglist, owner_id):
        """
        :param name: 
        :param price: 
        :param quantity: 
        :param shoppinglist: The shoppinglist this Item Belongs to 
        """
        self.name = name
        self.price = price
        self.quantity = quantity
        self.shoppinglist_id = shoppinglist.id
        self.owner_id = owner_id

    def update_item(self, name, price, quantity, shoppinglist=None):
        # updates self
        if name != "None":
            self.name = name
        if price != 0:
            self.price = price
        if quantity != 0:
            self.quantity = quantity
        if shoppinglist is not None:
            self.shoppinglist_id = shoppinglist.id
        db.session.commit()
