from logging import getLogger, DEBUG, Formatter, FileHandler, StreamHandler
from pathlib import Path

from common.string_common import get_caller_name, is_query_update
from config import bot_config


def get_logger(name):
  file_path = Path(bot_config.logs_path + name + '.log')
  Path(bot_config.logs_path).mkdir(parents=True, exist_ok=True)
  logger = getLogger(name)
  logger.setLevel(DEBUG)
  formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  file_handler = FileHandler(file_path, encoding='utf-8')
  file_handler.setFormatter(formatter)
  stream_handler = StreamHandler()
  stream_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  logger.addHandler(stream_handler)
  return logger


def get_last_name(update, query=False):
  if query:
    return ' {0}'.format(update.callback_query.message.chat.last_name) if update.callback_query.message.chat.last_name \
      else ''
  return ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else ''


def get_username(update, query=False):
  if not query:
    return ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else ''
  return ' - @{0} '.format(
    update.callback_query.message.chat.username) if update.callback_query.message.chat.username else ''


def log_update(update, local_logger):
  string_format = '{0} handler: message from {1}{2}{3}({4}) received: {5}'
  if is_query_update(update):
    local_logger.debug(string_format.format(get_caller_name(), update.callback_query.message.chat.first_name,
                                            get_last_name(update, query=True), get_username(update, query=True),
                                            update.callback_query.message.chat.id, update.callback_query.data))
  else:
    local_logger.debug(
      string_format.format(get_caller_name(), update.message.from_user.first_name, get_last_name(update),
                           get_username(update), update.message.from_user.id, update.message.text))
