import unittest

from app import create_app
from app.init_db import db

from app.models.user import User
from app.controller import save_user


class TestUser(unittest.TestCase):
    configurations = "testing"
    app = create_app(configurations)
    app.app_context().push()
    db.drop_all()
    db.create_all()

    def setUp(self):
        self.user = User(username="esir", email="esirkings@gmail.com", password="Andela2017")
        self.token = self.user.generate_auth_token(expiration=50, configurations=self.configurations)

    def test_set_password(self):
        """
        If set_password works then a password hash is stored
        """
        self.assertNotEqual(self.user.password, "Andela2017")

    def test_check_password(self):
        self.assertTrue(self.user.password,
                        self.user.check_password("Andela2017"))

    def test_token_generator(self):
        """
        test if a new token is generated after defined expiration time
        """
        self.assertNotEqual(
            self.user.generate_auth_token(expiration=100,
                                          configurations=self.configurations),
            self.user.generate_auth_token(expiration=300,
                                          configurations=self.configurations))

    def test_verify_auth_token(self):
        user = User(username="rick", email="picklerick@gmail.com", password="Andela2017")
        save_user(user)
        """
        Making expiration -1 to indicate expired token
        """
        tok1 = user.generate_auth_token(expiration=-1,
                                        configurations=self.configurations)

        from app.exceptions import TokenExpired, InvalidToken
        with self.assertRaises(InvalidToken):
            user.verify_auth_token("very_invalid_token",
                                   configuration=self.configurations)
        with self.assertRaises(TokenExpired):
            user.verify_auth_token(tok1,
                                   configuration=self.configurations)


if __name__ == '__main__':
    unittest.main()
