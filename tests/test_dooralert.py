import os
import unittest

from configparser import ConfigParser
from dooralert import TokenProvider

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

class TestTokenProviderWithNoConfigFile(unittest.TestCase):
    def test_config_file_name_is_none(self):
        with self.assertRaises(ValueError) as cm:
            TokenProvider(config_file_name=None)
        self.assertEqual(str(cm.exception), 'Config file name is none.')
    
    def test_config_file_does_not_exist(self):
        with self.assertRaises(FileNotFoundError) as cm:
            TokenProvider('unknown.txt')

class TestTokenProviderWithConfigFile(unittest.TestCase):
    telegram_bot_section = 'telegram.bot'
    telegram_bot_token_key = 'token'
    telegram_bot_token_value = 'some_token'
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_name = 'config/my.ini'
    real_config_file_name = os.path.join(current_dir, config_file_name)

    def create_config(telegram_bot_section, telegram_bot_token_key, telegram_bot_token_value):
        if os.path.exists(TestTokenProviderWithConfigFile.real_config_file_name):
            os.remove(TestTokenProviderWithConfigFile.real_config_file_name)
        os.makedirs(os.path.dirname(TestTokenProviderWithConfigFile.real_config_file_name), exist_ok=True)
        config = ConfigParser()
        config[telegram_bot_section] = {}
        config[telegram_bot_section][telegram_bot_token_key] = telegram_bot_token_value
        with open(TestTokenProviderWithConfigFile.real_config_file_name, 'w') as config_file:
            config.write(config_file)

    def setUp(self):
        TestTokenProviderWithConfigFile.create_config(TestTokenProviderWithConfigFile.telegram_bot_section, TestTokenProviderWithConfigFile.telegram_bot_token_key, TestTokenProviderWithConfigFile.telegram_bot_token_value)
    
    def tearDown(self):
        if os.path.exists(TestTokenProviderWithConfigFile.real_config_file_name):
            os.remove(TestTokenProviderWithConfigFile.real_config_file_name)
    
    def test_telegram_bot_section_is_none(self):
        token_provider = TokenProvider(TestTokenProviderWithConfigFile.real_config_file_name, telegram_bot_section=None)
        with self.assertRaises(KeyError) as cm:
            token_provider.get_token()

    def test_telegram_bot_token_key_is_none(self):
        token_provider = TokenProvider(TestTokenProviderWithConfigFile.real_config_file_name, telegram_bot_token_key=None)
        with self.assertRaises(KeyError) as cm:
            token_provider.get_token()

    def test_telegram_bot_default_config(self):
        token_provider = TokenProvider(TestTokenProviderWithConfigFile.real_config_file_name)
        token = token_provider.get_token()
        self.assertEqual(token, TestTokenProviderWithConfigFile.telegram_bot_token_value)
    
    def test_telegram_bot_custom_config(self):
        section = 'my.section'
        key = 'my_token'
        val = 'my_value'
        TestTokenProviderWithConfigFile.create_config('my.section', 'my_token', val)
        token_provider = TokenProvider(TestTokenProviderWithConfigFile.real_config_file_name, telegram_bot_section=section, telegram_bot_token_key=key)
        token = token_provider.get_token()
        self.assertEqual(token, val)

if __name__ == '__main__':
    unittest.main()