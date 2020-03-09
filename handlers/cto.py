import subprocess

from bot_daemon import logger, is_user_authorized
from logger import log_update
from string_common import is_vlan_id_valid


def cto(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      update.message.reply_text(
        'Envie "/cto 1234" para receber o relatório da ONU de ID 1234. Envie "/cto 1234 tecnico" para receber o mesmo '
        'relatório, mas ordenado por endereço em vez de nome.',
        quote=True)
    elif is_vlan_id_valid(context.args[0]):
      command_list = ['python3.8', 'cto_info.py', '-c', '{0}'.format(context.args[0])]
      if args_len == 2 and context.args[1].lower() == 'tecnico':
        command_list.extend(['-t', '1'])
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('cto: answer_string: {0}'.format(answer_string))
    else:
      update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /cto.', quote=True)
