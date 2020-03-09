import inspect
import logging

import bot_config
from string_common import get_caller_name

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(bot_config.logs_path + __name__)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def is_query_update(update):
  try:
    update.message.chat
    return False
  except:
    return True


def get_last_name(update, query=False):
  if query:
    return ' {0}'.format(update.callback_query.message.chat.last_name) if update.callback_query.message.chat.last_name \
      else ''
  return ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else ''


def get_username(update, query=False):
  if query:
    return ' - @{0} '.format(update.callback_query.message.chat.username) if update.callback_query.message.chat.username \
      else ''
  return ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else ''


def log_update(update, logger):
  string_format = '{0} handler: message from {1}{2}{3}({4}) received: {5}'
  if is_query_update(update):
    logger.debug(string_format.format(get_caller_name(), update.callback_query.message.chat.first_name,
                                      get_last_name(update, query=True), get_username(update, query=True),
                                      update.callback_query.message.chat.id, update.callback_query.data))
  else:
    logger.debug(string_format.format(get_caller_name(), update.message.from_user.first_name, get_last_name(update),
                                      get_username(update), update.message.from_user.id, update.message.text))
