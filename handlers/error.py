from logger import log_update, logger


def error(update, context):
  logger.warning('Update "%s" caused error "%s"', update, context.error)
  log_update(update, logger)
