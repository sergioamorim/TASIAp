from logger import log_update, get_logger


logger = get_logger(__name__)


def help_handler(update):
  log_update(update, logger)
  update.message.reply_text('Menus disponíveis: \n/autorizar\n/sinal\n/reiniciar', quote=True)
