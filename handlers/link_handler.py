import subprocess

from bot_daemon import logger, is_user_authorized, create_link_changing_command_list


def link(update, context):
  logger.debug('link handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name,
                                                                                ' {0}'.format(
                                                                                  update.message.from_user.last_name) if update.message.from_user.last_name else '',
                                                                                ' - @{0} '.format(
                                                                                  update.message.from_user.username) if update.message.from_user.username else '',
                                                                                update.message.from_user.id,
                                                                                update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text(
        'Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois links.', quote=True)
    elif context.args[0] == 'squid':
      command_list = create_link_changing_command_list('first-link')
      logger.debug(command_list)
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
      update.message.reply_text('Comando enviado para usar apenas o link SQUID.', quote=True)
    elif context.args[0] == 'we':
      command_list = create_link_changing_command_list('second-link')
      logger.debug(command_list)
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
      update.message.reply_text('Comando enviado para usar apenas o link WE.', quote=True)
    elif context.args[0] == 'ambos':
      command_list = create_link_changing_command_list('both-links')
      logger.debug(command_list)
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
      update.message.reply_text('Comando enviado para usar ambos os links.', quote=True)
    else:
      update.message.reply_text(
        'Comando inválido. Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois '
        'links.',
        quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /link.', quote=True)