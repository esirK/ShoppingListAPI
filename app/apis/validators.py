import ast
import numbers
import re

from flask import jsonify


def name_validalidatior(name, context):
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


def price_quantity_validator(value, name):
    value = ast.literal_eval(value)
    if not isinstance(value, numbers.Number):
        response = {
            "errors": {
                name: "Item " + name + " has to be an Number"
            },
            "message": "Input payload validation failed"
        }
        return response, 400


def numbers_validator(value):
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
