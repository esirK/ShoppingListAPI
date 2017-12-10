import sqlalchemy
from sqlalchemy.orm import make_transient

from app.exceptions import UserAlreadyExist
from app.init_db import db
from app.models import ShoppingList, Item


def save_user(user):
    """
    Adds current user into the Database
    """
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise UserAlreadyExist
    return True


def update_user(user, username, password):
    """
        Updates A user Data. For account management
        """
    if password != "None":
        user.set_password(password)
    if username != "None":
        user.username = username
    db.session.commit()


def add_shopping_list(user, name, description):
    """
        Adds a ShoppingList to this user account
        """
    shopping_lst = ShoppingList.query.filter_by(name=name) \
        .filter_by(owner_id=user.id).first()
    if shopping_lst:
        # user has the shopping list
        return False

    shopping_list = ShoppingList(name=name, description=description,
                                 owner=user)

    db.session.add(shopping_list)
    db.session.commit()
    return True


def add_shared_shopping_list(shopping_list, share_with):
    # check if shopping list exist
    shopping_lst = ShoppingList.query.filter_by(id=shopping_list.id) \
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


def delete_shoppinglist(shoppinglist, items):
    db.session.delete(shoppinglist)
    for item in items:
        db.session.delete(item)

    db.session.commit()


def update_shopping_list(shoppinglist, name, description):
    """
        Updates Shopping List Data
        """
    if description is not '':
        shoppinglist.description = description
    if name is not '':
        shoppinglist.name = name
    db.session.commit()


def share(shoppinglist, shared, shared_by):
    shoppinglist.shared = shared
    shoppinglist.shared_by = shared_by
    db.session.commit()


def add_item(shoppinglist, name, price, quantity, owner_id):
    """
        Adds an item to the current shoppinglist
        """
    item = Item(name=name, price=price, quantity=quantity,
                shoppinglist=shoppinglist, owner_id=owner_id)
    check_item = Item.query.filter_by(name=name). \
        filter_by(shoppinglist_id=shoppinglist.id).first()
    if not check_item:
        db.session.add(item)
        db.session.commit()
        return True
    else:
        return False


def delete_item(item):
    """
        Deletes an item from this shopping list
        :param item:
        """
    db.session.delete(item)
    db.session.commit()
