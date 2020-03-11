from inspect import stack
from logging import getLogger, DEBUG, Formatter, FileHandler, StreamHandler
from pathlib import Path
from re import findall

from common.string_common import get_caller_name, is_query_update
from config import bot_config

if result := findall('.*/(.*?).py', stack()[-1].filename):
  module_name = result[0]
else:
  module_name = stack()[-1].filename[:-3]

logger = getLogger(module_name)
logger.setLevel(DEBUG)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_path = Path(bot_config.logs_path + module_name + '.log')
Path(bot_config.logs_path).mkdir(parents=True, exist_ok=True)
file_handler = FileHandler(file_path)
file_handler.setFormatter(formatter)
stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


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
