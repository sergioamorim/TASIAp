from telegram import ParseMode

from bot_daemon import logger, is_user_authorized
from common.string_common import format_clients_message
from logger import log_update
from username_by_name import find_username_by_name


def procurar(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text(
        'Envie "/procurar maria" para receber a lista de clientes que contenham maria no nome, endereço, '
        'login ou observações.',
        quote=True)
    else:
      name = ' '.join(context.args)
      update.message.reply_text(format_clients_message(name, find_username_by_name(name)), parse_mode=ParseMode.HTML,
                                quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /procurar.', quote=True)
