from subprocess import run

from common.bot_common import is_user_authorized
from config import bot_config
from logger import log_update, get_logger

logger = get_logger(__name__)


def create_link_changing_command_list(link_name):
  return ['ssh', '-p', '{0}'.format(bot_config.mk_link['ssh']['port']), '-i',
          '{0}'.format(bot_config.mk_link['ssh']['identity_file']),
          '{0}@{1}'.format(bot_config.mk_link['ssh']['user'], bot_config.mk_link['ssh']['ip']), '/system', 'script',
          'run', '{0}'.format(bot_config.mk_link['script'][link_name])]


def link(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text(
        'Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois links.', quote=True)
    elif context.args[0] == 'squid':
      command_list = create_link_changing_command_list('first-link')
      logger.debug(command_list)
      answer_string = run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
      update.message.reply_text('Comando enviado para usar apenas o link SQUID.', quote=True)
    elif context.args[0] == 'we':
      command_list = create_link_changing_command_list('second-link')
      logger.debug(command_list)
      answer_string = run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
      update.message.reply_text('Comando enviado para usar apenas o link WE.', quote=True)
    elif context.args[0] == 'ambos':
      command_list = create_link_changing_command_list('both-links')
      logger.debug(command_list)
      answer_string = run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
      update.message.reply_text('Comando enviado para usar ambos os links.', quote=True)
    else:
      update.message.reply_text(
        'Comando inválido. Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois '
        'links.',
        quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /link.', quote=True)
