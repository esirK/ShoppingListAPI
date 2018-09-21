class TokenExpired(Exception):
    """
    This Will be raised incases where a token is valid but expired 
    """
    pass


class InvalidToken(Exception):
    """
    This Will be raised incases where a token is invalid 
    """
    pass


class UserAlreadyExist(Exception):
    """
    This Will be raised incases where a user already exist in the db 
    """
    pass
