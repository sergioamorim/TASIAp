from bot_daemon import logger
from logger import log_update


def general(update):
  log_update(update, logger)
  update.message.reply_text(
    'Não entendi. Utilize um dos menus para executar funções. Utilize o handlers /help para mais informações.',
    quote=True)
