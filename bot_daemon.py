#!/usr/bin/env python3.8
# coding=utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.constants import MAX_MESSAGE_LENGTH
import logging
import re
import subprocess
import bot_config
from onu_id_from_username import find_onu_by_user
import inspect
from user_from_onu import is_cto_id
from onu_signal_power import get_onu_power_signal_by_id
from mysql_common import get_mysql_session, user_exists
from telnetlib import Telnet
import telnet_config
from telnet_common import connect_su
from string_common import is_onu_id_valid, is_vlan_id_valid, is_serial_valid, is_int, get_onu_id_from_repr, remove_accents, sanitize_dumb
from onu_id_from_serial import find_onu_by_serial
from user_from_onu import find_user_by_onu
from find_next_onu_connection import find_onu_connection
from threading import Thread
from username_by_name import find_username_by_name

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
  return True if user_id in bot_config.permissions[inspect.stack()[1].function] else False

def create_link_changing_command_list(link):
  return ['ssh', '-p', '{0}'.format(bot_config.mk_link['ssh']['port']), '{0}@{1}'.format(bot_config.mk_link['ssh']['user'], bot_config.mk_link['ssh']['ip']), '/system',  'script', 'run', '{0}'.format(bot_config.mk_link['script'][link])]

def create_keyboard_markup_auth(onu_serials_list):
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

def format_clients_message(name, result):
  message = ''
  for client in result['direct']:
    message = message+'Nome: <u>{0}</u>\nEndereço: {1}, {2}\n<b>Usuário:</b> <code>{3}</code>\n'.format(client['nome'], client['endereco'], client['numero'], client['user'])
  message = message+'\n'
  for client in result['related']:
    message = message+'Nome: <u>{0}</u>\nEndereço: {1}, {2}\n'.format(client['nome'], client['endereco'], client['numero'])
    name = remove_accents(name.lower())
    if name in client['complemento'].lower():
      message = message+'Complemento: {0}\n'.format(sanitize_dumb(client['complemento']))
    if name in client['referencia'].lower():
      message = message+'Referencia: {0}\n'.format(sanitize_dumb(client['referencia']))
    if name in client['observacao'].lower():
      message = message+'Observacao: {0}\n'.format(sanitize_dumb(client['observacao']))
    message = message+'<b>Usuário:</b> <code>{0}</code>\n'.format(client['user'])
  if (message_len := len(message)) > 1:
    if message_len > MAX_MESSAGE_LENGTH:
      message = message[:MAX_MESSAGE_LENGTH-18]+'\n\n<b>CROPED!</b>'
    return message
  return 'Nenhum cliente encontrado com o termo informado.'

def get_signal(onu_id):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    signal = get_onu_power_signal_by_id(tn, onu_id)
  if signal == 'not found':
    return 'não existe ONU autorizada com esse ID.'
  elif signal == 'off':
    return 'sem sinal.'
  elif signal == 'error':
    return 'erro não especificado.'
  return signal

def get_message_from_update(update):
  try:
    update.message.chat
    return update.message
  except:
    return update.callback_query.message

def callback_signal_job(context):
  signal = get_signal(context.job.context['onu_id'])
  context.bot.send_message(context.job.context['chat_id'], 'Sinal: {0}'.format(signal), reply_to_message_id=context.job.context['message_id'])
  if context.job.context['chat_id'] != int(bot_config.default_chat):
    context.bot.send_message(int(bot_config.default_chat), 'ONU ID: {0}\nSinal: {1}'.format(context.job.context['onu_id'], signal))

def signal_job_caller(context, update, onu_id):
  message = get_message_from_update(update)
  job_context = {'chat_id': message.chat.id, 'onu_id': onu_id, 'message_id': message.message_id}
  context.job_queue.run_once(callback_signal_job, 10, context=job_context)
  return 'ainda em processo de autorização, o sinal será enviado em 10 segundos.'

def find_onu_connection_trigger(bot, update, onu_id):
  message = get_message_from_update(update)
  if (connection_info := find_onu_connection(onu_id)):
    message_text = 'Roteador conectado na ONU ID {0}.\nUsuário: {1}\nSenha: {2}\nStatus da conexão: {3}'.format(onu_id, connection_info['username'], connection_info['password'], connection_info['diagnostic'])
  else:
    message_text = 'Nenhum roteador foi conectado na ONU ID {0}.'.format(onu_id)
  bot.send_message(message.chat.id, message_text, reply_to_message_id=message.message_id)
  if message.chat.id != int(bot_config.default_chat):
    bot.send_message(int(bot_config.default_chat), message_text)

def get_onu_info_string(context, update, onu_repr=None, onu_id=None, cvlan=None, serial=None):
  signal = None
  if onu_repr:
    onu_repr_pattern = "([0-9A-Z]{4}[0-9A-Fa-f]{8})',pon='<Pon\(pon_id='[0-9]',board='<Board\(board_id='[0-9]{2}'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='[0-9]+',cvlan='(N?o?n?e?[0-9]{0,4})"
    regex_result = re.findall(onu_repr_pattern, onu_repr)
    serial = regex_result[0][0]
    if regex_result[0][1] != 'None':
      cvlan = regex_result[0][1]
    onu_id = get_onu_id_from_repr(onu_repr)
    signal = signal_job_caller(context, update, onu_id)
  else:
    signal = get_signal(onu_id)
    if signal == 'sem sinal.':
      signal = signal_job_caller(context, update, onu_id)
  if cvlan and cvlan[2:] == '00' and cvlan != '4000':
    Thread(target=find_onu_connection_trigger, args=(context.bot, update, onu_id)).start()
  return 'ID: {0}{1}\nSerial: {2}{3}'.format(onu_id, '\nCVLAN: {0}'.format(cvlan) if cvlan else '', serial, '\nSinal: {0}'.format(signal))

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
      update.message.reply_text('Envie "/sinal 1234" para verificar o sinal da ONU de ID 1234, "/sinal maria" para verificar o sinal da ONU do usuário maria ou "/sinal FHTT0fab320e" para verificar o sinal da ONU com serial FHTT0fab320e.', quote=True)
    session = get_mysql_session()
    if is_onu_id_valid(context.args[0]):
      cto_string = is_cto_id(session, context.args[0])
      signal = get_signal(context.args[0]).capitalize()
      update.message.reply_text('{0}{1}'.format('{0}\n'.format(cto_string) if cto_string else '', signal), quote=True)
    elif (serial := re.findall("([0-9A-Z]{4}[0-9A-Fa-f]{8})", context.args[0])):
      if (onu := find_onu_by_serial(serial[0])):
        cto_string = is_cto_id(session, onu['onuid'])
        if onu['state'] == 'dn':
          update.message.reply_text('{0}ONU ID: {1}\nSem sinal.'.format('{0}\n'.format(cto_string) if cto_string else '', onu['onuid']), quote=True)
        else:
          signal = get_signal(onu['onuid']).capitalize()
          update.message.reply_text('{0}ONU ID: {1}\n{2}'.format('{0}\n'.format(cto_string) if cto_string else '', onu['onuid'], signal), quote=True)
      else:
        update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
    elif user_exists(session, context.args[0]):
      onu_id = find_onu_by_user(context.args[0])
      if onu_id['onu_id']:
        signal = get_signal(onu_id['onu_id']).capitalize()
        onu_reference = 'ONU da {0}: '.format(onu_id['cto_name']) if onu_id['cto_name'] else 'ONU ID {0}: '.format(onu_id['onu_id'])
        update.message.reply_text('{0}{1}\nSinal da {2}{3}'.format(onu_reference, onu_id['diagnostic'], onu_reference, signal), quote=True)
      elif onu_id['diagnostic']:
        update.message.reply_text('{0}\nTente novamente informando o ID ou serial da ONU.'.format(onu_id['diagnostic']), quote=True)
      else:
        update.message.reply_text('Nenhuma conexão do usuário informado foi encontrada.\nTente novamente informando o ID ou serial da ONU.', quote=True)
    else:
      update.message.reply_text('ID da ONU, usuário ou serial inválido ou não encontrado.', quote=True)
    session.close()
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /sinal.', quote=True)

def reiniciar(update, context):
  logger.debug('reiniciar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/reiniciar 1234" para reiniciar a ONU de ID 1234.', quote=True)
    elif is_onu_id_valid(context.args[0]):
      keyboard = [[
        InlineKeyboardButton(text='Confirmar', callback_data="<a=r><i={0}>".format(context.args[0])),
        InlineKeyboardButton(text='Cancelar', callback_data="<a=ar>")
      ]]
      keyboard_markup = InlineKeyboardMarkup(keyboard)
      text = 'Tem certeza que deseja reiniciar a ONU de ID *{0}*?'.format(context.args[0])
      update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, quote=True, reply_markup=keyboard_markup)
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
        keyboard_markup = create_keyboard_markup_auth(answer_list)
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
        update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(context, update, onu_repr=answer_string)), quote=True)
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
        update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(context, update, onu_repr=answer_string)), quote=True)
      elif 'ERR' in answer_string:
        update.message.reply_text('A ONU não foi encontrada. Envie /authorize para ver a lista de ONUs disponíveis.', quote=True)
      elif 'None' in answer_string:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /authorize para verificar novamente.', quote=True)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /authorize.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /authorize.', quote=True)

def procurar(update, context):
  logger.debug('procurar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/procurar maria" para receber a lista de clientes que contenham maria no nome, endereço, login ou observações.', quote=True)
    else:
      name = ' '.join(context.args)
      update.message.reply_text(format_clients_message(name, find_username_by_name(name)), parse_mode=ParseMode.HTML, quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /procurar.', quote=True)

def usuario(update, context):
  logger.debug('usuario handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      update.message.reply_text('Envie "/usuario 1234" para verificar o usuário da ONU de ID 1234 ou "/usuario FHTT0fab320e" para verificar o usuário da ONU de serial FHTT0fab320e.', quote=True)
    else:
      if is_onu_id_valid(context.args[0]):
        if (user := find_user_by_onu(context.args[0])):
          if user == 'ERR':
            update.message.reply_text('Nenhuma ONU encontrada com esse ID.', quote=True)
          else:
            update.message.reply_text(user, quote=True)
        else:
          update.message.reply_text('Nenhum usuário associado à ONU foi encontrado.', quote=True)
      elif is_serial_valid(context.args[0]):
        if (onu := find_onu_by_serial(context.args[0])):
          session = get_mysql_session()
          cto_string = is_cto_id(session, context.args[0])
          session.close()
          if onu['state'] == 'dn':
            update.message.reply_text('ONU ID: {0}\nSem sinal.{1}'.format(onu['onuid'], '\n{0}'.format(cto_string) if cto_string else ''), quote=True)
          else:
            if (user := find_user_by_onu(onu['onuid'])):
              update.message.reply_text('ONU ID: {0}\n{1}'.format(onu['id'], user), quote=True)
            else:
              update.message.reply_text('ONU ID: {0}\nNenhum usuário associado à ONU foi encontrado.'.format(onu['onuid']), quote=True)
        else:
          update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
      else:
        update.message.reply_text('ID ou serial da ONU inválido.', quote=True)
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
      update.message.reply_text('Envie "/vlan 1234 1200" para configurar a ONU de ID 1234 com a CVLAN 1200.', quote=True)
    elif is_onu_id_valid(context.args[0]):
      if (args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1]):
        keyboard = [[
          InlineKeyboardButton(text='Confirmar', callback_data="<a=v><i={0}><v={1}>".format(context.args[0], args_1_lower)),
          InlineKeyboardButton(text='Cancelar', callback_data="<a=av>")
        ]]
        keyboard_markup = InlineKeyboardMarkup(keyboard)
        text = 'Tem certeza que deseja configurar a ONU de ID *{0}* com a CVLAN *{1}*?'.format(context.args[0], context.args[1])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, quote=True, reply_markup=keyboard_markup)
      else:
        update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.', quote=True)
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /cto.', quote=True)

def onuid(update, context):
  logger.debug('onuid handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    if len(context.args) != 1:
      update.message.reply_text('Envie "/onuid usuariologin" para verificar o ID da ONU do usuario "usuariologin".', quote=True)
    else:
      session = get_mysql_session()
      if is_serial_valid(context.args[0]):
        if (onu := find_onu_by_serial(context.args[0])):
          update.message.reply_text(onu['id'], quote=True)
        else:
          update.message.reply_text('Nenhuma ONU encontrada com o serial informado.', quote=True)
      else:
        onu_id = find_onu_by_user(context.args[0])
        if onu_id['onu_id']:
          onu_reference = 'ONU da {0}'.format(onu_id['cto_name']) if onu_id['cto_name'] else 'ONU ID {0}'.format(onu_id['onu_id'])
          update.message.reply_text('{0}{1}'.format(onu_reference, onu_id['diagnostic']), quote=True)
        elif onu_id['diagnostic']:
          update.message.reply_text('{0}\nTente novamente informando o serial da ONU.'.format(onu_id['diagnostic']), quote=True)
        else:
          update.message.reply_text('Nenhuma conexão do usuário informado foi encontrada.\nTente novamente informando o serial da ONU.', quote=True)
      session.close()
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
      if query.message.chat.id != int(bot_config.default_chat):
        context.bot.send_message(int(bot_config.default_chat), '{0} autorizando {1} {2}'.format(query.message.chat.id, onu_id, serial))
      query.edit_message_text('ONU de cliente ou CTO?', reply_markup=keyboard_markup, quote=True)
    elif answer_string == 'ERR':
      query.edit_message_text('Tente novamente, não foi possivel encontrar a ONU informada agora. Envie /autorizar para ver a lista de ONUs disponíveis.', quote=True)
    elif answer_string == 'None':
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
    onu_info_string = get_onu_info_string(context, update, onu_id=onu_id, cvlan=cvlan_commited, serial=serial)
    if query.message.chat.id != int(bot_config.default_chat):
      context.bot.send_message(int(bot_config.default_chat), '{0} autorizou\n{1}'.format(query.message.chat.id, onu_info_string))
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
      query.edit_message_text('Resposta desconhecida: {1}'.format(answer_string), quote=True)
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
    query.edit_message_text('ONU de ID {0} configurada com sucesso com a CVLAN {1}.'.format(onu_id, cvlan_commited), quote=True)
  elif action == 'av':
    query.edit_message_text('Configuração de CVLAN cancelada.', quote=True)

def main():
  updater = Updater(bot_config.token, use_context=True)

  updater.dispatcher.add_handler(CommandHandler("start", start))
  updater.dispatcher.add_handler(CommandHandler("autorizar", autorizar))
  updater.dispatcher.add_handler(CommandHandler("authorize", authorize))
  updater.dispatcher.add_handler(CommandHandler("sinal", sinal))
  updater.dispatcher.add_handler(CommandHandler("reiniciar", reiniciar))
  updater.dispatcher.add_handler(CommandHandler("procurar", procurar))
  updater.dispatcher.add_handler(CommandHandler("usuario", usuario))
  updater.dispatcher.add_handler(CommandHandler("onuid", onuid))
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
