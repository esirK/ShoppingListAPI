import re

from flask import jsonify


def name_validalidatior(name, context, update=None):
    if update is not None:
        if name is '':
            name = "None"
    """Method used to validate various names"""
    if len(name.strip()) == 0 or not re.match("^[-a-zA-Z0-9_\\s]*$", name):
        response = {
            "message": "Name shouldn't be empty. And No special "
                       "characters Allowed" + " for " + context + " names"
        }
        return response, 400
    if name.isdigit():
        response = {
            "message": "Name shouldn't be Numbers Alone."
        }
        return response, 400


def price_quantity_validator(value, name, update=None):
    if update is not None:
        if value is '':
            value = 0.0
    if not validate_floats(value):
        response = {
            "errors": {
                name: "Item " + name + " has to be an Number"
            },
            "message": "Input payload validation failed"
        }
        return response, 400


def numbers_validator(value, update=None):
    if update is not None:
        if value is '':
            value = 0
    if not str(value).isdigit():
        response = {
            "message": "An Invalid id type was provided. Expecting Integers only"
        }
        return response, 400


def password_validator(password):
    reg_pass = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$"
    if not re.search(reg_pass, password):
        response = {
            'message': 'Password Must be at least 6 '
                       'characters both numbers and letters'
        }
        response = jsonify(response)
        response.status_code = 400
        return response


def validate_ints(value):
    if len(value) > 10:
        return False
    try:
        int(value)
        return True
    except ValueError:
        return False


def validate_floats(value):
    if value is None:
        value = "0.0"
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_values(name, price, quantity, shopping_list, update=None):
    errors = {}
    invalid_name = name_validalidatior(name, "Shopping List Item", update)
    if invalid_name:
        errors.update({'name': invalid_name})
    invalid_price = price_quantity_validator(price, "Price", update)
    if invalid_price:
        errors.update({'price': invalid_price})

    invalid_quantity = price_quantity_validator(quantity, "Quantity", update)
    if invalid_quantity:
        errors.update({'quantity': invalid_quantity})
    if shopping_list is not None:
        invalid_id = numbers_validator(shopping_list)
        if invalid_id:
            errors.update({'id': invalid_id})
    return errors
