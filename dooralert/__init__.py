import os.path

from functools import wraps
from configparser import ConfigParser
from telebot import TeleBot
from telebot.types import Message
from telebot.apihelper import ApiException

from dooralert.logger import get_logger
from dooralert.bot_message_handler import BotMessageHandler

__version__ = "0.0.1"
logger = get_logger(__name__)


class DoorAlertBotException(Exception):
    pass

def log(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        function_name = f.__name__
        logger.debug('Entering {0} function. Args: {1}; Kwargs: {2}'.format(function_name, args, kwargs))
        ret = f(*args, **kwargs)
        logger.debug('Leaving {0} function.'.format(function_name))
        return ret
    return decorated



class TokenProvider:
    def __init__(self, config_file_name, telegram_bot_section='telegram.bot', telegram_bot_token_key='token'):
        if config_file_name is None:
            msg = 'Config file name is none.'
            logger.critical(msg)
            raise ValueError(msg)
        if not os.path.isfile(config_file_name):
            expected_path = os.path.abspath('.')
            msg = 'Config file "{0}" does not exist in directory {1}'.format(config_file_name, expected_path)
            logger.critical(msg)
            raise FileNotFoundError(msg)
        self._config_file_name = config_file_name
        self._telegram_bot_section = telegram_bot_section
        self._telegram_bot_token_key = telegram_bot_token_key
    
    def get_token(self):
        logger.debug('Reading config file: {}'.format(self._config_file_name))
        _config = ConfigParser()
        _config.read(self._config_file_name)
        logger.debug('done.')

        logger.debug('Try to find section {} in config file.'.format(self._telegram_bot_section))
        _telegram_bot_section_present = (not self._telegram_bot_section is None) and self._telegram_bot_section in _config
        if not _telegram_bot_section_present:
            _error_msg = 'Section {0} is not present in the {1} file.'.format(self._telegram_bot_section, self._config_file_name)
            logger.error(_error_msg)
            raise KeyError(_error_msg)
        logger.debug('done.')
        
        logger.debug('Try to find key {0} of section {1} in config file.'.format(self._telegram_bot_token_key, self._telegram_bot_section))
        _telegram_bot_token_key_is_present = (not self._telegram_bot_token_key is None) and self._telegram_bot_token_key in _config[self._telegram_bot_section]
        if not _telegram_bot_token_key_is_present:
            _error_msg = 'Section {0} has no {1} key in the {1} file.'.format(self._telegram_bot_section, self._telegram_bot_token_key, self._config_file_name)
            logger.error(_error_msg)
            raise KeyError(_error_msg)
        logger.debug('done.')

        logger.debug('Try to create bot connection with token.')
        return _config[self._telegram_bot_section][self._telegram_bot_token_key]

class DoorAlertBot:
    def __init__(self, config_provider: TokenProvider, telegram_bot_message_handler: BotMessageHandler):
        self._config_provider = config_provider
        self._message_handler = telegram_bot_message_handler
        self._bot = None
    
    def init_bot(self):
        token = self._config_provider.get_token()
        self._bot = TeleBot(token=token)
    
    def contains_chat(self, chat_id):
        return self._message_handler.contains_chat(chat_id)
    
    def get_chat(self, chat_id):
        self._check_bot_initialized()
        return self._bot.get_chat(chat_id)
    
    def get_chat_administrators(self, chat_id):
        self._check_bot_initialized()
        return self._bot.get_chat_administrators(chat_id)
    
    def process_new_messages(self, messages: list):
        self._check_bot_initialized()
        self._bot.process_new_messages(messages)

    def _check_bot_initialized(self):
        bot = self._bot
        if bot is None:
            msg = 'Bot is not initialized.'
            logger.critical(msg)
            raise DoorAlertBotException(msg)

    def init_handlers(self):
        self._check_bot_initialized()
        bot = self._bot
        bot_message_handler = self._message_handler

        @bot.message_handler(commands=['start', 'welcome'])
        @log
        def send_welcome(message):
            bot_message_handler.handle_welcome(bot, message)

        @bot.message_handler(commands=['help'])
        @log
        def send_help(message):
            bot_message_handler.handle_help(bot, message)

        @bot.message_handler(commands=['subscribe'])
        @log
        def subscribe_chat(message):
            bot_message_handler.handle_subscribe_chat(bot, message)

        @bot.message_handler(commands=['subscriptions'])
        @log
        def get_subscriptions(message):
            bot_message_handler.handle_get_subscriptions(bot, message)

        @bot.message_handler(commands=['unsubscribe'])
        @log
        def unsubscribe_chat(message):
            bot_message_handler.handle_unsubscribe_chat(bot, message)

        #### Just some test
        def find_at(msg):
            for text in msg:
                if '@' in text:
                    return text


        @bot.message_handler(func=lambda msg: msg.text is not None and '@' in msg.text)
        @log
        def at_answer(message):
            texts = message.text.split()
            at_text = find_at(texts)
            bot.reply_to(message, 'https://instagram.com/{}'.format(at_text[1:]))
        #### End

    def polling(self, *args, **kwargs):
        logger.info("Start polling...")
        self._bot.polling(*args, **kwargs)
        logger.info("Polling ended.")