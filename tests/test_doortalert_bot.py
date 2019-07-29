import unittest
import time
import os

from parameterized import parameterized, parameterized_class
from telebot import types, util, TeleBot
from dooralert import DoorAlertBot, DoorAlertBotException
from dooralert.bot_message_handler import BotMessageHandler


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

class TestDoorAlertUtils:
    @staticmethod
    def create_text_message(text, user=None):
        params = {'text': text}
        chat = types.User(11, False, 'test') if user is None else user 
        return types.Message(1, None, None, chat, 'text', params, "")

    @staticmethod
    def create_group_text_message(text, bot: TeleBot, chat_id):
        params = {'text': text}
        chat = bot.get_chat(chat_id)
        from_user = TestDoorAlertUtils.get_chat_administrator(bot, chat_id)
        return types.Message(1, from_user, None, chat, 'text', params, "")
    
    @staticmethod
    def get_chat_administrator(bot: TeleBot, chat_id):
        users = bot.get_chat_administrators(chat_id)
        if len(users) is 0:
            raise RuntimeError('There should be at least one administrator in the group.')
        return users[0]


class TestDoorAlertBotLogic(unittest.TestCase):
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

        msg = TestDoorAlertUtils.create_text_message(message)
        bot = dooralert_bot.bot
        bot.process_new_messages([msg])
        time.sleep(1)
        self.assertEqual(msg.text, result)
    
    def test_init_handlers_before_init_bot(self):
        token = 'token'
        token_provider = MockTokenProvider(token)
        message_handler = MockBotMessageHandler()
        dooralert_bot = DoorAlertBot(token_provider, message_handler)
        with self.assertRaises(DoorAlertBotException) as cm:
            dooralert_bot.init_handlers()


class TestDoorAlertBot(unittest.TestCase):
    def setUp(self):
        chat_id = os.environ['TELEGRAM_CHAT_ID']
        token = os.environ['TELEGRAM_BOT_TOKEN']

        token_provider = MockTokenProvider(token)
        message_handler = BotMessageHandler()
        dooralert_bot = DoorAlertBot(token_provider, message_handler)
        dooralert_bot.init_bot()
        dooralert_bot.init_handlers()
        
        self._dooralert_bot = dooralert_bot
        self._internal_bot = dooralert_bot.bot
        self._chat_id = chat_id

    def test_valid_subscribe(self):
        bot = self._internal_bot
        msg = TestDoorAlertUtils.create_group_text_message('/subscribe', bot, self._chat_id)
        bot.process_new_messages([msg])
        msg = TestDoorAlertUtils.create_group_text_message('/subscriptions', bot, self._chat_id)
        bot.process_new_messages([msg])
        contains_chat = self._dooralert_bot.contains_chat(self._chat_id)
        self.assertTrue(contains_chat)
    
    def test_unsubscribe_after_valid_subscribe(self):
        bot = self._internal_bot
        msg = TestDoorAlertUtils.create_group_text_message('/subscribe', bot, self._chat_id)
        bot.process_new_messages([msg])
        msg = TestDoorAlertUtils.create_group_text_message('/unsubscribe', bot, self._chat_id)
        bot.process_new_messages([msg])
        msg = TestDoorAlertUtils.create_group_text_message('/subscriptions', bot, self._chat_id)
        bot.process_new_messages([msg])
        contains_chat = self._dooralert_bot.contains_chat(self._chat_id)
        self.assertFalse(contains_chat)


if __name__ == '__main__':
    unittest.main()
