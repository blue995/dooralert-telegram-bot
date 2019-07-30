import logging.handlers
import os
import errno


try:
    _LOG_DIR = os.environ['LOG_DIR']
except KeyError:
    _LOG_DIR = 'logs'

all_loggers = []

if not os.path.isdir(_LOG_DIR):
    try:
        os.makedirs(_LOG_DIR)
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


def get_logger_name(name=None):
    if name:
        return '{}'.format(name)
    return 'root'


def get_logger(name=None):
    real_logger_name = get_logger_name(name)
    logger = logging.getLogger(real_logger_name)
    if not real_logger_name in all_loggers:
        init_logger(logger)
        all_loggers.append(real_logger_name)
    return logger


def init_logger(logger):
    # Default logger log level
    default_logger_log_level = logging.DEBUG
    logger.setLevel(default_logger_log_level)

    # Default message format
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Outputs debug log messages to the console.
    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    # Saves error messages in error.log
    error_handler = logging.handlers.RotatingFileHandler('{dir}/error.log'.format(dir=_LOG_DIR), maxBytes=1024*10, backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Saves info messages in app.log
    general_file_handler = logging.handlers.RotatingFileHandler('{dir}/app.log'.format(dir=_LOG_DIR), maxBytes=1024*10, backupCount=3)
    general_file_handler.setLevel(logging.INFO)
    general_file_handler.setFormatter(formatter)
    logger.addHandler(general_file_handler)
