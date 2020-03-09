from bot_daemon import logger
from logger import log_update


def start(update):
  log_update(update, logger)
  update.message.reply_text('Menus disponíveis:\n/autorizar\n/sinal\n/reiniciar\n\nAjuda em /help', quote=True)
