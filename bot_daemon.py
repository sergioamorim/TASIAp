#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
import logging
import re
import subprocess
import bot_config

logger = logging.getLogger('bot_daemon')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/bot_daemon.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def is_user_authorized(user_id):
  return True if user_id in bot_config.authorized_users else False

def is_onu_id_valid(onu_id):
  return is_int(onu_id) and int(onu_id) > 1100 and int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9

def is_vlan_id_valid(vlan_id):
  return is_int(vlan_id) and int(vlan_id) > 0 and int(vlan_id) < 4096

def create_link_changing_command_list(link):
  return ['ssh', '-p', '{0}'.format(bot_config.mk_link['ssh']['port']), '{0}@{1}'.format(bot_config.mk_link['ssh']['user'], bot_config.mk_link['ssh']['ip']), '/system',  'script', 'run', '{0}'.format(bot_config.mk_link['script'][link])]

def create_keyboard_markup(onu_serials_list):
  keyboard = []
  for onu_serial in onu_serials_list:
    onu_serial_regex_list = re.findall('(.*)_(.*)_(.*)', onu_serial)
    board = onu_serial_regex_list[0][0]
    pon = onu_serial_regex_list[0][1]
    serial = onu_serial_regex_list[0][2]
    callback_data = "<a=ca><s={0}><b={1}><p={2}>".format(serial, board, pon)
    keyboard.append([InlineKeyboardButton(text='Serial: {0} Placa: {1} PON: {2}'.format(serial, board, pon), callback_data=callback_data)])
  keyboard.append([InlineKeyboardButton(text='Cancelar', callback_data="<a=aa>")])
  keyboard_markup = InlineKeyboardMarkup(keyboard)
  return keyboard_markup

def get_signal(onu_id):
  command_list = ['python3.8', 'onu_signal_power.py', '-i', '{0}'.format(onu_id)]
  logger.debug('get_signal: command_list: {0}'.format(command_list))
  answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
  logger.debug('get_signal: answer_string: {0}'.format(answer_string))
  if answer_string == 'not found':
    return 'não existe ONU autorizada com esse ID'
  elif answer_string == 'off':
    return 'sem sinal'
  elif answer_string == 'error':
    return 'erro não especificado'
  return answer_string

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def get_onu_info_string(onu_repr=None, onu_id=None, cvlan=None, serial=None):
  signal = None
  if onu_repr:
    onu_repr_pattern = "([0-9A-Z]{4}[0-9A-Fa-f]{8})',pon='<Pon\(pon_id='[0-9]',board='<Board\(board_id='[0-9]{2}'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='[0-9]+',cvlan='(N?o?n?e?[0-9]{0,4})"
    regex_result = re.findall(onu_repr_pattern, onu_repr)
    serial = regex_result[0][0]
    if (cvlan := regex_result[0][1]) != 'None':
      cvlan = cvlan[0]
    onu_id = get_onu_id_from_repr(onu_repr)
  else:
    signal = get_signal(onu_id)
  return 'ID: {0}{1}\nSerial: {2}{3}'.format(onu_id, '\nVLAN: {0}'.format(cvlan) if cvlan else '', serial, '\nSinal: {0}'.format(signal) if signal else '')

def get_onu_id_from_repr(onu_repr):
  onu_repr_pattern = "([0-9])',board='<Board\(board_id='([0-9]{2})'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='([0-9]+)"
  regex_result = re.findall(onu_repr_pattern, onu_repr)
  board = regex_result[0][1]
  pon = regex_result[0][0]
  onu_number = regex_result[0][2]
  onu_id = '{0}{1}{2}{3}'.format('1' if board == '12' else '2', pon, '0' if int(onu_number) < 10 else '', onu_number)
  return onu_id

def start(update, context):
  logger.debug('start handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  update.message.reply_text('Menus disponíveis:\n/autorizar\n/sinal\n/reiniciar\n\nAjuda em /help', quote=True)

def help(update, context):
  logger.debug('help handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  update.message.reply_text('Menus disponíveis: \n/autorizar\n/sinal\n/reiniciar', quote=True)

def sinal(update, context):
  logger.debug('sinal handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Comando inválido. Envie "/sinal 1234" para verificar o sinal da ONU de ID 1234.', quote=True)
    if is_onu_id_valid(context.args[0]):
      signal = get_signal(context.args[0])
      update.message.reply_text(signal.capitalize(), quote=True)
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /sinal.', quote=True)

def reiniciar(update, context):
  logger.debug('reiniciar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/reiniciar 1234" para reiniciar a ONU de ID 1234.', quote=True)
    elif is_onu_id_valid(context.args[0]):
      command_list = ['python3.8', 'onu_restart.py', '-i', '{0}'.format(context.args[0])]
      logger.debug('reiniciar handler: valid id: command_list: {0}'.format(command_list))
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
      logger.debug('reiniciar handler: valid id: answer_string: {0}'.format(answer_string))
      if answer_string == 'not found':
        update.message.reply_text('Sem sinal ou não existe ONU autorizada com esse ID.', quote=True)
      elif answer_string == 'error':
        update.message.reply_text('Erro não especificado.', quote=True)
      elif answer_string == 'done':
        update.message.reply_text('Comando enviado com sucesso. A ONU será reiniciada em até 2 minutos.', quote=True)
      else:
        update.message.reply_text('Resposta desconhecida: {1}'.format(answer_string), quote=True)
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /reiniciar.', quote=True)

def autorizar(update, context):
  logger.debug('autorizar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      answer_list = subprocess.run(['python3.8', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(' ')
      logger.debug('autorizar handler: /autorizar: answer_list: {0}'.format(answer_list))
      if '\n' in answer_list:
        answer_list.remove('\n')
      if len(answer_list) == 1 and 'None' in answer_list[0]:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /autorizar para verificar novamente se há novas ONUs.', quote=True)
      else:
        keyboard_markup = create_keyboard_markup(answer_list)
        update.message.reply_text('Confirme os dados da ONU que deseja autorizar:', quote=True, reply_markup=keyboard_markup)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /autorizar.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /autorizar.', quote=True)

def authorize(update, context):
  logger.debug('authorize handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      answer_list = subprocess.run(['python3.8', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(' ')
      logger.debug('authorize handler: /authorize: answer_list: {0}'.format(answer_list))
      if '\n' in answer_list:
        answer_list.remove('\n')
      if len(answer_list) == 1:
        if 'None' in answer_list[0]:
          update.message.reply_text('Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente se há novas ONUs.', quote=True)
        else:
          update.message.reply_text('Uma ONU foi encontrada: '+answer_list[0]+'\nConfirma serial para autorizar?\nEnvie "/authorize sim" para autorizar ou /authorize para verificar novamente se há novas ONUs.', quote=True)
      else:
        reply_list = []
        for i, answer in enumerate(answer_list):
          reply_list.append(str(i+1)+'. ')
          reply_list.append(answer+'\n')
        update.message.reply_text('ONUs encontradas:\n'+''.join(reply_list)+'Envie o número da ONU que deseja autorizar (ex.: "/authorize 1") ou /authorize para verificar novamente se há novas ONUs.', quote=True)
    elif is_int(context.args[0]):
      if args_len == 2 and ((args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1])):
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '{0}'.format(context.args[0]), '-c', '{0}'.format(args_1_lower)], capture_output=True).stdout.decode('utf-8')
      else:
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '{0}'.format(context.args[0])], capture_output=True).stdout.decode('utf-8')
      logger.debug('authorize: int: answer_string: {0}'.format(answer_string))
      if 'OnuDevice' in answer_string:
        update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(onu_repr=answer_string)), quote=True)
      elif 'ERR' in answer_string:
        update.message.reply_text('A ONU informada não foi encontrada. Envie /authorize para ver a lista de ONUs disponíveis.', quote=True)
      elif 'None' in answer_string:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente se há novas ONUs.', quote=True)
    elif context.args[0] == 'sim':
      if args_len == 2 and ((args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1])):
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '1', '-c', '{0}'.format(args_1_lower)], capture_output=True).stdout.decode('utf-8')
      else:
        answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '1'], capture_output=True).stdout.decode('utf-8')
      logger.debug('authorize: sim: answer_string: {0}'.format(answer_string))
      if 'OnuDevice' in answer_string:
        update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(onu_repr=answer_string)), quote=True)
      elif 'ERR' in answer_string:
        update.message.reply_text('A ONU não foi encontrada. Envie /authorize para ver a lista de ONUs disponíveis.', quote=True)
      elif 'None' in answer_string:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente.', quote=True)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /authorize.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /authorize.', quote=True)

def usuario(update, context):
  logger.debug('usuario handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/usuario 1234" para verificar o usuário da ONU de ID 1234.', quote=True)
    elif is_onu_id_valid(context.args[0]):
      answer_string = subprocess.run(['python3.8', 'user_from_onu.py', '-i', '{0}'.format(context.args[0])], capture_output=True).stdout.decode('utf-8')
      logger.debug('usuario: answer_string: {0}'.format(answer_string))
      if 'None' in answer_string:
        update.message.reply_text('Nenhum usuário associado à ONU foi encontrado.', quote=True)
      elif 'ERR' in answer_string:
        update.message.reply_text('Nenhuma ONU encontrada com este ID.', quote=True)
      else:
        update.message.reply_text('{0}'.format(answer_string), quote=True)
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /usuario.', quote=True)

def cto(update, context):
  logger.debug('cto handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not (args_len := len(context.args)):
      update.message.reply_text('Envie "/cto 1234" para receber o relatório da ONU de ID 1234. Envie "/cto 1234 tecnico" para receber o mesmo relatório, mas ordenado por endereço em vez de nome.', quote=True)
    elif is_vlan_id_valid(context.args[0]):
      command_list = ['python3.8', 'cto_info.py', '-c', '{0}'.format(context.args[0])]
      if args_len == 2 and context.args[1].lower() == 'tecnico':
        command_list.extend(['-t', '1'])
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
      logger.debug('cto: answer_string: {0}'.format(answer_string))
    else:
      update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /cto.', quote=True)

def vlan(update, context):
  logger.debug('vlan handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if len(context.args) != 2:
      update.message.reply_text('Envie "/vlan 1234 1200" para configurar como 1200 a CVLAN da ONU de ID 1234.', quote=True)
    elif is_onu_id_valid(context.args[0]):
      if (args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1]):
        command_list = ['python3.8', 'onu_set_cvlan.py', '-i', '{0}'.format(context.args[0]), '-c', '{0}'.format(args_1_lower)]
        answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
        logger.debug('vlan: answer_string: {0}'.format(answer_string))
        cvlan_commited = re.findall('_([0-9]{4})', answer_string)[0]
        update.message.reply_text('CVLAN da ONU de ID {0} configurada com sucesso para {1}'.format(context.args[0], cvlan_commited), quote=True)
      else:
        update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.', quote=True)
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /cto.', quote=True)

def link(update, context):
  logger.debug('link handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois links.', quote=True)
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
      update.message.reply_text('Comando inválido. Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois links.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /link.', quote=True)

def error(update, context):
  logger.warning('Update "%s" caused error "%s"', update, context.error)
  logger.debug('error handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))

def general(update, context):
  logger.debug('general handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  update.message.reply_text('Não entendi. Utilize um dos menus para executar funções. Utilize o menu /help para mais informações.', quote=True)

def button(update, context):
  query = update.callback_query
  logger.debug('button handler: query from {0}{1}{2}({3}) received: {4}'.format(query.message.chat.first_name, ' {0}'.format(query.message.chat.last_name) if query.message.chat.last_name else '', ' - @{0} '.format(query.message.chat.username) if query.message.chat.username else '', query.message.chat.id, query.data))
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
    query.edit_message_text('Tem certeza que deseja autorizar a ONU de serial *{0}* na *placa {1} PON {2}*?'.format(serial, board, pon), reply_markup=keyboard_markup, parse_mode=ParseMode.MARKDOWN, quote=True)
  elif action == 'a':
    serial = re.findall('<s=(.*?)>', query.data)[0]
    answer_string = subprocess.run(['python3.8', 'authorize_onu.py', '-a', '{0}'.format(serial)], capture_output=True).stdout.decode('utf-8')
    logger.debug('button: authorize: answer_string: {0}'.format(answer_string))
    if 'OnuDevice' in answer_string:
      serial = re.findall("([0-9A-Z]{4}[0-9A-Fa-f]{8})", answer_string)[0]
      onu_id = get_onu_id_from_repr(answer_string)
      callback_data = '<a=c><s={0}><i={1}>'.format(serial, onu_id)
      keyboard = [[
        InlineKeyboardButton(text='CTO', callback_data='{0}{1}'.format(callback_data, '<c=ct>')),
        InlineKeyboardButton(text='Cliente', callback_data='{0}{1}'.format(callback_data, '<c=cl>'))
      ]]
      keyboard_markup = InlineKeyboardMarkup(keyboard)
      query.edit_message_text('ONU de cliente ou CTO?', reply_markup=keyboard_markup, quote=True)
    elif 'ERR' in answer_string:
      query.edit_message_text('Tente novamente, não foi possivel encontrar a ONU informada agora. Envie /autorizar para ver a lista de ONUs disponíveis.', quote=True)
    elif 'None' in answer_string:
      query.edit_message_text('Tente novamente, não foi possivel encontrar nenhuma ONU agora. Envie /autorizar para verificar novamente se há ONUs disponíveis.', quote=True)
  elif action == 'c':
    data_pattern = '<s=(.*?)><i=(.*?)><c=(.*?)>'
    regex_result = re.findall(data_pattern, query.data)
    serial = regex_result[0][0]
    onu_id = regex_result[0][1]
    cvlan = regex_result[0][2]
    command_list = ['python3.8', 'onu_set_cvlan.py', '-i', '{0}'.format(onu_id)]
    if cvlan == 'ct':
      command_list.extend(['-c', 'cto'])
    logger.debug('button: set_cvlan: command_list: {0}'. format(command_list))
    answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
    logger.debug('button: set_cvlan: answer_string: {0}'. format(answer_string))
    cvlan_commited = re.findall('_([0-9]{4})', answer_string)[0]
    onu_info_string = get_onu_info_string(onu_id=onu_id, cvlan=cvlan_commited, serial=serial)
    query.edit_message_text('ONU autorizada com sucesso!\n{0}'.format(onu_info_string), quote=True)
  elif action == 'aa':
    query.edit_message_text('Autorização cancelada.', quote=True)

def main():
  updater = Updater(bot_config.token, use_context=True)

  updater.dispatcher.add_handler(CommandHandler("start", start))
  updater.dispatcher.add_handler(CommandHandler("autorizar", autorizar))
  updater.dispatcher.add_handler(CommandHandler("authorize", authorize))
  updater.dispatcher.add_handler(CommandHandler("sinal", sinal))
  updater.dispatcher.add_handler(CommandHandler("reiniciar", reiniciar))
  updater.dispatcher.add_handler(CommandHandler("usuario", usuario))
  updater.dispatcher.add_handler(CommandHandler("cto", cto))
  updater.dispatcher.add_handler(CommandHandler("vlan", vlan))
  updater.dispatcher.add_handler(CommandHandler("link", link))
  updater.dispatcher.add_handler(CallbackQueryHandler(button))
  updater.dispatcher.add_handler(CommandHandler("help", help))
  updater.dispatcher.add_handler(MessageHandler(Filters.text, general))

  updater.dispatcher.add_error_handler(error)

  logger.info('Starting...')
  updater.start_polling()

  updater.idle()

if __name__ == '__main__':
  main()