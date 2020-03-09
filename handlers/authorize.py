import subprocess

from bot_daemon import logger, is_user_authorized, get_onu_info_string
from string_common import is_int, is_vlan_id_valid


def authorize(update, context):
  logger.debug(
    'authorize handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name,
                                                                          ' {0}'.format(
                                                                            update.message.from_user.last_name) if update.message.from_user.last_name else '',
                                                                          ' - @{0} '.format(
                                                                            update.message.from_user.username) if update.message.from_user.username else '',
                                                                          update.message.from_user.id,
                                                                          update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      answer_list = subprocess.run(['python3.8', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(
        ' ')
      logger.debug('authorize handler: /authorize: answer_list: {0}'.format(answer_list))
      if '\n' in answer_list:
        answer_list.remove('\n')
      if len(answer_list) == 1:
        if 'None' in answer_list[0]:
          update.message.reply_text(
            'Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente se há novas ONUs.', quote=True)
        else:
          update.message.reply_text('Uma ONU foi encontrada: ' + answer_list[
            0] + '\nConfirma serial para autorizar?\nEnvie "/authorize sim" para autorizar ou /authorize para '
                 'verificar novamente se há novas ONUs.',
                                    quote=True)
      else:
        reply_list = []
        for i, answer in enumerate(answer_list):
          reply_list.append(str(i + 1) + '. ')
          reply_list.append(answer + '\n')
        update.message.reply_text('ONUs encontradas:\n' + ''.join(
          reply_list) + 'Envie o número da ONU que deseja autorizar (ex.: "/authorize 1") ou /authorize para '
                        'verificar novamente se há novas ONUs.',
                                  quote=True)
    elif is_int(context.args[0]):
      if args_len == 2 and ((args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1])):
        answer_string = subprocess.run(
          ['python3.8', 'authorize_onu.py', '-a', '{0}'.format(context.args[0]), '-c', '{0}'.format(args_1_lower)],
          capture_output=True).stdout.decode('utf-8')
      else:
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '{0}'.format(context.args[0])],
                                       capture_output=True).stdout.decode('utf-8')
      logger.debug('authorize: int: answer_string: {0}'.format(answer_string))
      if 'OnuDevice' in answer_string:
        update.message.reply_text(
          'ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(context, update, onu_repr=answer_string)),
          quote=True)
      elif 'ERR' in answer_string:
        update.message.reply_text(
          'A ONU informada não foi encontrada. Envie /authorize para ver a lista de ONUs disponíveis.', quote=True)
      elif 'None' in answer_string:
        update.message.reply_text(
          'Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente se há novas ONUs.', quote=True)
    elif context.args[0] == 'sim':
      if args_len == 2 and ((args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1])):
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '1', '-c', '{0}'.format(args_1_lower)],
                                       capture_output=True).stdout.decode('utf-8')
      else:
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '1'], capture_output=True).stdout.decode(
          'utf-8')
      logger.debug('authorize: sim: answer_string: {0}'.format(answer_string))
      if 'OnuDevice' in answer_string:
        update.message.reply_text(
          'ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(context, update, onu_repr=answer_string)),
          quote=True)
      elif 'ERR' in answer_string:
        update.message.reply_text('A ONU não foi encontrada. Envie /authorize para ver a lista de ONUs disponíveis.',
                                  quote=True)
      elif 'None' in answer_string:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente.', quote=True)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /authorize.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /authorize.', quote=True)