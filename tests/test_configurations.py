import os
import unittest

from app import config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.dev_config = config['development']
        self.testing_config = config['testing']
        self.production_config = config['production']

    def test_development_config(self):
        """Test For Configurations Required For Development"""
        self.assertTrue(self.dev_config.DEBUG is True)
        self.assertTrue(
            self.dev_config.SQLALCHEMY_DATABASE_URI == os.environ.get('DEVDB'))
        self.assertFalse(self.dev_config.SECRET_KEY is 'wireless')

    def test_testing_config(self):
        """Test For Configurations Required For Testing"""
        self.assertTrue(self.testing_config.DEBUG)
        self.assertTrue(self.testing_config.TESTING)

    def test_production_config(self):
        """Test For Configurations Required For Production"""
        self.assertFalse(self.production_config.DEBUG)
        self.assertFalse(self.production_config.TESTING)


if __name__ == '__main__':
    unittest.main()
