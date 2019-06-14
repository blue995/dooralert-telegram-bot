import time

from dooralert import BotInitializer, TokenProvider, DoorAlertBot

if __name__ == '__main__':
    config_file_name = 'dooralertbot.ini'
    telegram_bot_section = 'telegram.bot'
    telegram_bot_token_key = 'token'

    bot_initializer = BotInitializer()
    config_provider = TokenProvider(config_file_name=config_file_name, telegram_bot_section=telegram_bot_section, telegram_bot_token_key=telegram_bot_token_key)
    bot = DoorAlertBot(config_provider=config_provider, telegram_bot_initializer=bot_initializer)

    bot.init_bot()
    bot.init_handlers()
    bot.polling(none_stop=True)
