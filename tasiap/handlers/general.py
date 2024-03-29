from tasiap.logger import log_update, get_logger

logger = get_logger(__name__)


# noinspection PyUnusedLocal
def general(update, context):
  log_update(update, logger)
  update.message.reply_text(
    'Não entendi. Utilize um dos menus para executar funções. Utilize o menu /help para mais informações.',
    quote=True)
