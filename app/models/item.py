from datetime import datetime

from app import db


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    price = db.Column(db.Integer())
    quantity = db.Column(db.Integer())
    shoppinglist_id = db.Column(db.Integer, db.ForeignKey('shoppinglists.id'))
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, name, price, quantity, shoppinglist):
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
