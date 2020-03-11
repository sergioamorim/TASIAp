from re import findall

from common.bot_common import is_user_authorized, get_signal
from common.mysql_common import get_mysql_session, user_exists
from common.string_common import is_onu_id_valid
from logger import log_update, get_logger
from onu_id_from_serial import find_onu_by_serial
from onu_id_from_username import find_onu_by_user
from user_from_onu import is_cto_id


logger = get_logger(__name__)


def sinal(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/sinal 1234" para verificar o sinal da ONU de ID 1234, "/sinal maria" para '
                                'verificar o sinal da ONU do usuário maria ou "/sinal FHTT0fab320e" para verificar o '
                                'sinal da ONU com serial FHTT0fab320e.', quote=True)
    session = get_mysql_session()
    if is_onu_id_valid(context.args[0]):
      cto_string = is_cto_id(session, context.args[0])
      signal = get_signal(context.args[0]).capitalize()
      update.message.reply_text('{0}{1}'.format('{0}\n'.format(cto_string) if cto_string else '', signal), quote=True)
    elif serial := findall("([0-9A-Z]{4}[0-9A-Fa-f]{8})", context.args[0]):
      if onu := find_onu_by_serial(serial[0]):
        cto_string = is_cto_id(session, onu['onuid'])
        if onu['state'] == 'dn':
          update.message.reply_text(
            '{0}ONU ID: {1}\nSem sinal.'.format('{0}\n'.format(cto_string) if cto_string else '', onu['onuid']),
            quote=True)
        else:
          signal = get_signal(onu['onuid']).capitalize()
          update.message.reply_text(
            '{0}ONU ID: {1}\n{2}'.format('{0}\n'.format(cto_string) if cto_string else '', onu['onuid'], signal),
            quote=True)
      else:
        update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
    elif user_exists(session, context.args[0]):
      onu_id = find_onu_by_user(context.args[0])
      if onu_id['onu_id']:
        signal = get_signal(onu_id['onu_id'])
        onu_reference = 'ONU da {0}: '.format(onu_id['cto_name']) if onu_id['cto_name'] else 'ONU ID {0}: '.format(
          onu_id['onu_id'])
        update.message.reply_text(
          '{0}{1}\nSinal da {2}{3}'.format(onu_reference, onu_id['diagnostic'], onu_reference, signal), quote=True)
      elif onu_id['diagnostic']:
        update.message.reply_text('{0}\nTente novamente informando o ID ou serial da ONU.'.format(onu_id['diagnostic']),
                                  quote=True)
      else:
        update.message.reply_text(
          'Nenhuma conexão do usuário informado foi encontrada.\nTente novamente informando o ID ou serial da ONU.',
          quote=True)
    else:
      update.message.reply_text('ID da ONU, usuário ou serial inválido ou não encontrado.', quote=True)
    session.close()
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /sinal.', quote=True)
