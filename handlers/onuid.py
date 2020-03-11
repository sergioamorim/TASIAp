from common.bot_common import is_user_authorized
from common.mysql_common import get_mysql_session
from common.string_common import is_serial_valid
from logger import log_update, logger
from onu_id_from_serial import find_onu_by_serial
from onu_id_from_username import find_onu_by_user


def onuid(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if len(context.args) != 1:
      update.message.reply_text('Envie "/onuid usuariologin" para verificar o ID da ONU do usuario "usuariologin".',
                                quote=True)
    else:
      session = get_mysql_session()
      if is_serial_valid(context.args[0]):
        if onu := find_onu_by_serial(context.args[0]):
          update.message.reply_text(onu['id'], quote=True)
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
      session.close()
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /cto.', quote=True)
