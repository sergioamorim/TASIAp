from tasiap.logger import log_update, get_logger

logger = get_logger(__name__)


# noinspection PyUnusedLocal
def start(update, context):
  log_update(update, logger)
  update.message.reply_text('Menus disponíveis:\n/autorizar\n/sinal\n/reiniciar\n\nAjuda em /help', quote=True)
