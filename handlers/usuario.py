from bot_daemon import logger, is_user_authorized
from mysql_common import get_mysql_session
from onu_id_from_serial import find_onu_by_serial
from string_common import is_onu_id_valid, is_serial_valid
from user_from_onu import find_user_by_onu, is_cto_id


def usuario(update, context):
  logger.debug('usuario handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name,
                                                                                   ' {0}'.format(
                                                                                     update.message.from_user.last_name) if update.message.from_user.last_name else '',
                                                                                   ' - @{0} '.format(
                                                                                     update.message.from_user.username) if update.message.from_user.username else '',
                                                                                   update.message.from_user.id,
                                                                                   update.message.text))
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
          session = get_mysql_session()
          cto_string = is_cto_id(session, context.args[0])
          session.close()
          if onu['state'] == 'dn':
            update.message.reply_text(
              'ONU ID: {0}\nSem sinal.{1}'.format(onu['onuid'], '\n{0}'.format(cto_string) if cto_string else ''),
              quote=True)
          else:
            if user := find_user_by_onu(onu['onuid']):
              update.message.reply_text('ONU ID: {0}\n{1}'.format(onu['id'], user), quote=True)
            else:
              update.message.reply_text(
                'ONU ID: {0}\nNenhum usuário associado à ONU foi encontrado.'.format(onu['onuid']), quote=True)
        else:
          update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
      else:
        update.message.reply_text('ID ou serial da ONU inválido.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /usuario.', quote=True)