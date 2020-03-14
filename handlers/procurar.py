from telegram import ParseMode

from common.bot_common import is_user_authorized
from common.string_common import format_clients_message
from cto_by_name import find_cto_by_name
from logger import log_update, get_logger
from username_by_name import find_username_by_name

logger = get_logger(__name__)


def procurar(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      update.message.reply_text(
        'Envie "/procurar maria" para receber a lista de clientes que contenham maria no nome, endereço, '
        'login ou observações. Envie "/procurar cto leisiane" para procurar CTOs com leisiane no nome.',
        quote=True)
    else:
      if context.args[0] == 'cto':
        if args_len > 1:
          update.message.reply_text('{0}'.format('/n'.join(find_cto_by_name(context.args[1:]))), quote=True)
        else:
          update.message.reply_text('Envie "/procurar cto leisiane" para procurar CTOs com leisiane no nome.',
                                    quote=True)
      else:
        name = ' '.join(context.args)
        update.message.reply_text(format_clients_message(name, find_username_by_name(name)), parse_mode=ParseMode.HTML,
                                  quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /procurar.', quote=True)
