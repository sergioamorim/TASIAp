from bot_daemon import logger
from logger import log_update


def error(update, context):
  logger.warning('Update "%s" caused error "%s"', update, context.error)
  log_update(update, logger)
