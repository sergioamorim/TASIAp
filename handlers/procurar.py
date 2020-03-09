from telegram import ParseMode

from bot_daemon import logger, is_user_authorized, format_clients_message
from username_by_name import find_username_by_name


def procurar(update, context):
  logger.debug('procurar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name,
                                                                                    ' {0}'.format(
                                                                                      update.message.from_user.last_name) if update.message.from_user.last_name else '',
                                                                                    ' - @{0} '.format(
                                                                                      update.message.from_user.username) if update.message.from_user.username else '',
                                                                                    update.message.from_user.id,
                                                                                    update.message.text))
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