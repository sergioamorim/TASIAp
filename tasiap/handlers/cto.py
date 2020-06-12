from tasiap import cto_info
from tasiap.common.bot_common import is_user_authorized
from tasiap.common.string_common import is_vlan_id_valid
from tasiap.logger import log_update, get_logger

logger = get_logger(__name__)


def cto(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      update.message.reply_text(
        'Envie "/cto 1234" para receber o relatório da ONU de ID 1234. Envie "/cto 1234 tecnico" para receber o mesmo '
        'relatório, mas ordenado por endereço em vez de nome.',
        quote=True)
    elif is_vlan_id_valid(context.args[0]):
      tech_report = True if args_len == 2 and context.args[1].lower() == 'tecnico' else False
      cto_info.do_things(cto_id=context.args[0], tech_report=tech_report)
    else:
      update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /cto.', quote=True)
