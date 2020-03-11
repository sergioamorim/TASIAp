from logger import log_update, get_logger


logger = get_logger(__name__)


def general(update):
  log_update(update, logger)
  update.message.reply_text(
    'Não entendi. Utilize um dos menus para executar funções. Utilize o handlers /help para mais informações.',
    quote=True)
