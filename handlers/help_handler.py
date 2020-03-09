from bot_daemon import logger
from logger import log_update


def help_handler(update):
  log_update(update, logger)
  update.message.reply_text('Menus disponíveis: \n/autorizar\n/sinal\n/reiniciar', quote=True)
