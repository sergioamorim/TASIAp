from bot_daemon import logger


def error(update, context):
  logger.warning('Update "%s" caused error "%s"', update, context.error)
  logger.debug('error handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name,
                                                                                 ' {0}'.format(
                                                                                   update.message.from_user.last_name) if update.message.from_user.last_name else '',
                                                                                 ' - @{0} '.format(
                                                                                   update.message.from_user.username) if update.message.from_user.username else '',
                                                                                 update.message.from_user.id,
                                                                                 update.message.text))
