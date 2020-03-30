from authorize_onu import authorize_onu
from common.bot_common import is_user_authorized, get_onu_info_string
from common.string_common import is_int, is_vlan_id_valid
from logger import log_update, get_logger

logger = get_logger(__name__)


def get_onu_text_list(onu_list):
  onu_text_list = ''
  for onu in onu_list:
    onu_text_list = onu_text_list + '{0}. Placa: {1} PON: {2} Serial: {3}\n'.format(onu.authorization_id,
                                                                                    onu.pon.board.board_id,
                                                                                    onu.pon.pon_id, onu.phy_id)
  return onu_text_list


def authorize(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      if onu_list := authorize_onu():
        update.message.reply_text('ONUs encontradas:\n{0}\nEnvie "/authorize 1" para autorizar a ONU número 1 da '
                                  'lista. Envie "/authorize 1 4000" para autorizar a ONU número 1 da lista e '
                                  'configurá-la com a CVLAN 4000.'.format(get_onu_text_list(onu_list)), quote=True)
      else:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente se há novas '
                                  'ONUs.', quote=True)
    elif is_int(context.args[0]):
      if args_len == 2 and (context.args[1].lower() == 'cto' or is_vlan_id_valid(context.args[1])):
        authorized_onu = authorize_onu(context.args[0], context.args[1].lower())
      else:
        authorized_onu = authorize_onu(context.args[0])
      if authorized_onu:
        if authorized_onu != 'ERROR':
          update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(
            get_onu_info_string(context, update, authorized_onu=authorized_onu)), quote=True)
        else:
          update.message.reply_text(
            'A ONU informada não foi encontrada. Envie /authorize para ver a lista de ONUs disponíveis.', quote=True)
      else:
        update.message.reply_text(
          'Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente se há novas ONUs.', quote=True)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /authorize.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /authorize.', quote=True)
