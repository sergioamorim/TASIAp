from tasiap.logger import log_update, get_logger

logger = get_logger(__name__)


def error(update, context):
  logger.warning('Update "%s" caused error "%s"', update, context.error)
  log_update(update, logger)
