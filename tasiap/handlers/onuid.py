from tasiap.common.bot_common import is_user_authorized
from tasiap.common.string_common import is_serial_valid
from tasiap.logger import log_update, get_logger
from tasiap.onu_id_from_serial import find_onu_by_serial
from tasiap.onu_id_from_username import find_onu_by_user

logger = get_logger(__name__)


def onuid(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if len(context.args) != 1:
      update.message.reply_text('Envie "/onuid maria" para verificar o ID da ONU do usuario usuariologin ou "/onuid '
                                'FHTT0fab320e" para verificar o ID da ONU de serial FHTT0fab320e.', quote=True)
    else:
      if is_serial_valid(context.args[0]):
        if onu := find_onu_by_serial(context.args[0]):
          update.message.reply_text(onu['onu_id'], quote=True)
        else:
          update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
      else:
        onu_id = find_onu_by_user(context.args[0])
        if onu_id['onu_id']:
          onu_reference = 'ONU da {0}'.format(onu_id['cto_name']) if onu_id['cto_name'] else 'ONU ID {0}'.format(
            onu_id['onu_id'])
          update.message.reply_text('{0}{1}'.format(onu_reference, onu_id['diagnostic']), quote=True)
        elif onu_id['diagnostic']:
          update.message.reply_text('{0}\nTente novamente informando o serial da ONU.'.format(onu_id['diagnostic']),
                                    quote=True)
        else:
          update.message.reply_text(
            'Nenhuma conexão do usuário informado foi encontrada.\nTente novamente informando o serial da ONU.',
            quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /cto.', quote=True)
