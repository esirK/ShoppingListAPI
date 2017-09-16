import unittest

from app.models.user import User


class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User(username="esir", email="esirkings@gmail.com", password="Andela2017")

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
        self.assertNotEqual(self.user.generate_auth_token(expiration=100),
                            self.user.generate_auth_token(expiration=300))


if __name__ == '__main__':
    unittest.main()
