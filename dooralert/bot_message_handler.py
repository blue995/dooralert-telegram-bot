from telebot import TeleBot

from dooralert.logger import get_logger


__version__ = "0.0.1"
logger = get_logger(__name__)

class BotMessageHandler:
    def __init__(self):
        self._subscriptions = set()
    
    def handle_welcome(self, bot: TeleBot, message):
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        welcome_msg = 'Welcome! {0} {1}'.format(first_name, last_name)
        logger.debug('Sending welcome reply to user: {}'.format(welcome_msg))
        bot.reply_to(message, welcome_msg)
        logger.debug('Calling send_help function.')
        self.handle_help(bot, message)
    
    def handle_help(self, bot: TeleBot, message):
        help_text = """
        Help for this bot:
        /help: Show this help.
        /subscribe: Subscribe this chat.
        /subscriptions: Get all subscribed chats.
        /start: Start the bot.
        /unsubscribe: Unsubscribe this chat.
        /welcome: Get the welcome message
        """
        logger.debug('Sending help reply to user.')
        bot.reply_to(message, help_text)

    def handle_subscribe_chat(self, bot: TeleBot, message):
        chat_id = message.chat.id
        logger.debug('Subscribing chat {}'.format(chat_id))
        self._subscriptions.add(chat_id)
        success_msg = 'Chat subscribed.'
        logger.debug('Sending success message to user: {}'.format(success_msg))
        bot.send_message(message.chat.id, success_msg)

    def handle_get_subscriptions(self, bot: TeleBot, message):
        chat_id = message.chat.id
        response = 'No chats subscribed yet.' if len(self._subscriptions) == 0 else ', '.join(str(e) for e in self._subscriptions)
        logger.debug('Sending response to user: {}'.format(response))
        bot.send_message(chat_id, response)

    def handle_unsubscribe_chat(self, bot: TeleBot, message):
        chat_id = message.chat.id
        logger.debug('Removing chat {}'.format(chat_id))
        if not chat_id in self._subscriptions:
            msg = 'This chat is not subscribed yet.'
        else:
            self._subscriptions.remove(chat_id)
            msg = 'Chat unsubscribed. You will no longer receive updates from this chat.'
        logger.debug('Sending message to user: {}'.format(msg))
        bot.send_message(message.chat.id, msg)
