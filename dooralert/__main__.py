import time
from configparser import ConfigParser
from telebot import TeleBot
from telebot.apihelper import ApiException
from dooralert.logger import get_logger


logger = get_logger()
config_file_name = 'dooralertbot.ini'
telegram_bot_section = 'telegram.bot'
telegram_bot_token_key = 'token'


def get_initialized_telegram_bot():
    logger.debug('Reading config file: {}'.format(config_file_name))
    _config = ConfigParser()
    _config.read(config_file_name)
    logger.debug('done.')

    logger.debug('Try to find section {} in config file.'.format(telegram_bot_section))
    _telegram_bot_section_present = telegram_bot_section in _config
    if not _telegram_bot_section_present:
        _error_msg = 'Section {0} is not present in the {1} file.'.format(telegram_bot_section, config_file_name)
        logger.error(_error_msg)
        raise KeyError(_error_msg)
    logger.debug('done.')
    
    logger.debug('Try to find key {0} of section {1} in config file.'.format(telegram_bot_token_key, telegram_bot_section))
    _telegram_bot_token_key_is_present = telegram_bot_token_key in _config[telegram_bot_section]
    if not _telegram_bot_token_key_is_present:
        _error_msg = 'Section {0} has no {1} key in the {1} file.'.format(telegram_bot_section, telegram_bot_token_key, config_file_name)
        logger.error(_error_msg)
        raise KeyError(_error_msg)
    logger.debug('done.')

    logger.debug('Try to create bot connection with token.')
    _bot_token = _config[telegram_bot_section][telegram_bot_token_key]
    _bot = TeleBot(token=_bot_token)
    logger.debug('done.')
    return _bot


bot = get_initialized_telegram_bot()
registered_chats = set()


@bot.message_handler(commands=['start', 'welcome'])
def send_welcome(message):
    logger.debug('Entering send_welcome function with message: {}'.format(message))
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    welcome_msg = 'Welcome! {0} {1}'.format(first_name, last_name)
    logger.debug('Sending welcome reply to user: {}'.format(welcome_msg))
    bot.reply_to(message, welcome_msg)
    logger.debug('Calling send_help function.')
    send_help(message)
    logger.debug('Leaving send_welcome function.')


@bot.message_handler(commands=['help'])
def send_help(message):
    logger.debug('Entering send_help function with message: {}'.format(message))
    help_text = """
    Help for this bot:
    /register: Register this current chat.
    /registered: Get all registered chats.
    /start: Start the bot.
    /welcome: Get the welcome message
    """
    logger.debug('Sending help reply to user.')
    bot.reply_to(message, help_text)
    logger.debug('Leaving send_help function.')


@bot.message_handler(commands=['register'])
def register_chat(message):
    logger.debug('Entering register_chat function with message: {}'.format(message))
    chat_id = message.chat.id
    logger.debug('Registering chat {}'.format(chat_id))
    registered_chats.add(chat_id)
    success_msg = 'Chat registered.'
    logger.debug('Sending success message to user: {}'.format(success_msg))
    bot.send_message(message.chat.id, success_msg)
    logger.debug('Leaving register_chat function.')


@bot.message_handler(commands=['registered'])
def get_registered_chats(message):
    logger.debug('Entering get_registered_chats function with message: {}'.format(message))
    chat_id = message.chat.id
    response = 'No chats registered yet.' if len(registered_chats) == 0 else ', '.join(str(e) for e in registered_chats)
    logger.debug('Sending response to user: {}'.format(response))
    bot.send_message(chat_id, response)
    logger.debug('Leaving get_registered_chats function.')


#### Just some test
def find_at(msg):
    for text in msg:
        if '@' in text:
            return text


@bot.message_handler(func=lambda msg: msg.text is not None and '@' in msg.text)
def at_answer(message):
    texts = message.text.split()
    at_text = find_at(texts)
    bot.reply_to(message, 'https://instagram.com/{}'.format(at_text[1:]))
#### End


logger.info("Start polling...")
bot.polling(none_stop=True)
logger.info("Polling ended.")