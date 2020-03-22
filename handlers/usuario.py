from common.bot_common import is_user_authorized
from common.mysql_common import supply_mysql_session
from common.string_common import is_onu_id_valid, is_serial_valid
from logger import log_update, get_logger
from onu_id_from_serial import find_onu_by_serial
from user_from_onu import find_user_by_onu, is_cto_id

logger = get_logger(__name__)


@supply_mysql_session
def usuario(update, context, session=None):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text(
        'Envie "/usuario 1234" para verificar o usuário da ONU de ID 1234 ou "/usuario FHTT0fab320e" para verificar o '
        'usuário da ONU de serial FHTT0fab320e.',
        quote=True)
    else:
      if is_onu_id_valid(context.args[0]):
        if user := find_user_by_onu(context.args[0]):
          if user == 'ERR':
            update.message.reply_text('Nenhuma ONU encontrada com esse ID.', quote=True)
          else:
            update.message.reply_text(user, quote=True)
        else:
          update.message.reply_text('Nenhum usuário associado à ONU foi encontrado.', quote=True)
      elif is_serial_valid(context.args[0]):
        if onu := find_onu_by_serial(context.args[0]):
          cto_string = is_cto_id(session, context.args[0])
          if onu['state'] == 'dn':
            update.message.reply_text(
              'ONU ID: {0}\nSem sinal.{1}'.format(onu['onu_id'], '\n{0}'.format(cto_string) if cto_string else ''),
              quote=True)
          else:
            if user := find_user_by_onu(onu['onu_id']):
              update.message.reply_text('ONU ID: {0}\n{1}'.format(onu['onu_id'], user), quote=True)
            else:
              update.message.reply_text(
                'ONU ID: {0}\nNenhum usuário associado à ONU foi encontrado.'.format(onu['onu_id']), quote=True)
        else:
          update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
      else:
        update.message.reply_text('ID ou serial da ONU inválido.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /usuario.', quote=True)
