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


def price_quantity_validator(value):
    if not str(value).isdigit():
            response = {
                "message": "Expecting Numbers Alone."
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