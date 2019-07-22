import unittest
import time

from parameterized import parameterized, parameterized_class
from telebot import types, util, TeleBot
from dooralert import DoorAlertBot, DoorAlertBotException


class MockBotMessageHandler:
    def handle_welcome(self, bot: TeleBot, message):
        message.text = 'welcome'
    
    def handle_help(self, bot: TeleBot, message):
        message.text = 'help'

    def handle_subscribe_chat(self, bot: TeleBot, message):
        message.text = 'subscribe'

    def handle_get_subscriptions(self, bot: TeleBot, message):
        message.text = 'subscriptions'
    
    def handle_unsubscribe_chat(self, bot: TeleBot, message):
        message.text = 'unsubscribe'


class MockTokenProvider:
    def __init__(self, token):
        self._token = token
    
    def get_token(self):
        return self._token

class TestTeleBot(unittest.TestCase):
    @parameterized.expand([
        ('token', '/help', 'help'),
        ('token', '/start', 'welcome'),
        ('token', '/subscribe', 'subscribe'),
        ('token', '/welcome', 'welcome'),
        ('token', '/subscriptions', 'subscriptions'),
        ('token', '/unsubscribe', 'unsubscribe')
    ])
    def test_full_message_handler_registration(self, token, message, result):
        token_provider = MockTokenProvider(token)
        message_handler = MockBotMessageHandler()
        dooralert_bot = DoorAlertBot(token_provider, message_handler)
        dooralert_bot.init_bot()
        dooralert_bot.init_handlers()

        msg = self.create_text_message(message)
        bot = dooralert_bot.bot
        bot.process_new_messages([msg])
        time.sleep(1)
        self.assertEqual(msg.text, result)


    @staticmethod
    def create_text_message(text):
        params = {'text': text}
        chat = types.User(11, False, 'test')
        return types.Message(1, None, None, chat, 'text', params, "")
    
    def test_init_handlers_before_init_bot(self):
        token = 'token'
        token_provider = MockTokenProvider(token)
        message_handler = MockBotMessageHandler()
        dooralert_bot = DoorAlertBot(token_provider, message_handler)
        with self.assertRaises(DoorAlertBotException) as cm:
            dooralert_bot.init_handlers()

if __name__ == '__main__':
    unittest.main()
