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
