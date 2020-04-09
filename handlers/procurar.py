from telegram import ParseMode

from common.bot_common import is_user_authorized
from common.string_common import format_clients_message, format_datetime
from cto_by_name import find_cto_by_name
from logger import log_update, get_logger
from username_by_name import find_username_by_name

logger = get_logger(__name__)


def get_readable_cto(cto):
  vlan_reference = ' (v{0})'.format(cto.vlan_id) if cto.vlan_id != cto.onu_id else ''
  last_connected_reference = ' (clientes offline desde {0})'.format(
                              format_datetime(cto.last_connected, readable=True)) if cto.last_connected else ''
  status_emoji = '❌' if cto.last_connected else '✅'
  return '{0} CTO {1}{2} {3}{4}'.format(status_emoji, cto.onu_id, vlan_reference, cto.cto_name,
                                        last_connected_reference)


def format_ctos_result(ctos_set):
  if ctos_set:
    return '\n'.join([get_readable_cto(cto) for cto in sorted(ctos_set, reverse=True)])
  return 'Nenhuma CTO encontrada com o nome informado.'


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
          cto_name = ' '.join(context.args[1:])
          formatted_ctos_result = format_ctos_result(find_cto_by_name(cto_name))
          update.message.reply_text(formatted_ctos_result, quote=True)
        else:
          update.message.reply_text('Envie "/procurar cto leisiane" para procurar CTOs com leisiane no nome.',
                                    quote=True)
      else:
        name = ' '.join(context.args)
        update.message.reply_text(format_clients_message(name, find_username_by_name(name)), parse_mode=ParseMode.HTML,
                                  quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /procurar.', quote=True)
