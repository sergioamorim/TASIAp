import re
import subprocess

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from bot_daemon import logger, get_onu_info_string
from common.sqlite_common import update_onu_info
from common.string_common import get_onu_id_from_repr
from config import bot_config
from logger import log_update


def button(update, context):
  log_update(update, logger)
  query = update.callback_query
  action = re.findall('<a=(.*?)>', query.data)[0]
  logger.debug('action: {0}'.format(action))
  if action == 'ca':
    data_pattern = '<s=(.*?)><b=(.*?)><p=(.*?)>'
    regex_result = re.findall(data_pattern, query.data)
    serial = regex_result[0][0]
    board = regex_result[0][1]
    pon = regex_result[0][2]
    callback_data = '<a=a><s={0}>'.format(serial)
    keyboard = [[
      InlineKeyboardButton(text='Confirmar', callback_data=callback_data),
      InlineKeyboardButton(text='Cancelar', callback_data='<a=aa>')
    ]]
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    logger.debug('keyboard_markup: {0}'.format(keyboard_markup))
    query.edit_message_text(
      'Tem certeza que deseja autorizar a ONU de serial *{0}* na *placa {1} PON {2}*?'.format(serial, board, pon),
      reply_markup=keyboard_markup, parse_mode=ParseMode.MARKDOWN, quote=True)
  elif action == 'a':
    serial = re.findall('<s=(.*?)>', query.data)[0]
    answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '{0}'.format(serial)],
                                   capture_output=True).stdout.decode('utf-8')
    logger.debug('button: authorize: answer_string: {0}'.format(answer_string))
    if 'OnuDevice' in answer_string:
      serial = re.findall("([0-9A-Z]{4}[0-9A-Fa-f]{8})", answer_string)[0]
      onu_id = get_onu_id_from_repr(answer_string)
      update_onu_info(int(onu_id), serial=serial)
      callback_data = '<a=c><s={0}><i={1}>'.format(serial, onu_id)
      keyboard = [[
        InlineKeyboardButton(text='CTO', callback_data='{0}{1}'.format(callback_data, '<c=ct>')),
        InlineKeyboardButton(text='Cliente', callback_data='{0}{1}'.format(callback_data, '<c=cl>'))
      ]]
      keyboard_markup = InlineKeyboardMarkup(keyboard)
      if query.message.chat.id != int(bot_config.default_chat):
        context.bot.send_message(int(bot_config.default_chat),
                                 '{0} autorizando {1} {2}'.format(query.message.chat.id, onu_id, serial))
      query.edit_message_text('ONU de cliente ou CTO?', reply_markup=keyboard_markup, quote=True)
    elif answer_string == 'ERR':
      query.edit_message_text(
        'Tente novamente, não foi possivel encontrar a ONU informada agora. Envie /autorizar para ver a lista de ONUs '
        'disponíveis.',
        quote=True)
    elif answer_string == 'None':
      query.edit_message_text(
        'Tente novamente, não foi possivel encontrar nenhuma ONU agora. Envie /autorizar para verificar novamente se '
        'há ONUs disponíveis.',
        quote=True)
  elif action == 'c':
    data_pattern = '<s=(.*?)><i=(.*?)><c=(.*?)>'
    regex_result = re.findall(data_pattern, query.data)
    serial = regex_result[0][0]
    onu_id = regex_result[0][1]
    cvlan = regex_result[0][2]
    command_list = ['python3.8', 'onu_set_cvlan.py', '-i', '{0}'.format(onu_id)]
    if cvlan == 'ct':
      command_list.extend(['-c', 'cto'])
    logger.debug('button: set_cvlan: command_list: {0}'.format(command_list))
    answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
    logger.debug('button: set_cvlan: answer_string: {0}'.format(answer_string))
    cvlan_commited = re.findall('_([0-9]{4})', answer_string)[0]
    onu_info_string = get_onu_info_string(context, update, onu_id=onu_id, cvlan=cvlan_commited, serial=serial)
    if query.message.chat.id != int(bot_config.default_chat):
      context.bot.send_message(int(bot_config.default_chat),
                               '{0} autorizou\n{1}'.format(query.message.chat.id, onu_info_string))
    query.edit_message_text('ONU autorizada com sucesso.\n{0}'.format(onu_info_string), quote=True)
  elif action == 'aa':
    query.edit_message_text('Autorização cancelada.', quote=True)
  elif action == 'r':
    onu_id = re.findall('<i=(.*?)>', query.data)[0]
    command_list = ['python3.8', 'onu_restart.py', '-i', '{0}'.format(onu_id)]
    logger.debug('button: reiniciar: valid id: command_list: {0}'.format(command_list))
    answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
    logger.debug('button: reiniciar: valid id: answer_string: {0}'.format(answer_string))
    if answer_string == 'not found':
      query.edit_message_text('Sem sinal ou não existe ONU autorizada com esse ID.', quote=True)
    elif answer_string == 'error':
      query.edit_message_text('Erro não especificado.', quote=True)
    elif answer_string == 'done':
      query.edit_message_text('Comando enviado com sucesso. A ONU será reiniciada em até 2 minutos.', quote=True)
    else:
      query.edit_message_text('Resposta desconhecida: {0}'.format(answer_string), quote=True)
  elif action == 'ar':
    query.edit_message_text('Reinicialização cancelada.', quote=True)
  elif action == 'v':
    data_pattern = '<i=(.*?)><v=(.*?)>'
    regex_result = re.findall(data_pattern, query.data)
    onu_id = regex_result[0][0]
    cvlan = regex_result[0][1]
    command_list = ['python3.8', 'onu_set_cvlan.py', '-i', '{0}'.format(onu_id), '-c', '{0}'.format(cvlan)]
    answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
    logger.debug('button: vlan: answer_string: {0}'.format(answer_string))
    cvlan_commited = re.findall('_([0-9]{4})', answer_string)[0]
    query.edit_message_text('ONU de ID {0} configurada com sucesso com a CVLAN {1}.'.format(onu_id, cvlan_commited),
                            quote=True)
  elif action == 'av':
    query.edit_message_text('Configuração de CVLAN cancelada.', quote=True)