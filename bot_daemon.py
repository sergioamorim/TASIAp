#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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

def is_int(s):
  try: 
    int(s)
    return True
  except ValueError:
    return False

def get_onu_info_string(onu_repr):
  phy_address = re.findall(".*phy_id\\=\\'([0-9A-Z]{4}[0-9A-Fa-f]{8}).*", onu_repr)[0]
  board = re.findall(".*board_id\\=\\'([0-9]{2}).*", onu_repr)[0]
  pon = re.findall(".*pon_id\\=\\'([0-9]).*", onu_repr)[0]
  onu_number = re.findall(".*number\\=\\'([0-9]*)'.*", onu_repr)[0]
  cvlan = re.findall(".*cvlan\\=\\'([0-9]*)'.*", onu_repr)[0]
  return '{0}{1}{2}{3} {4} {5}'.format('1' if board == '12' else '2', pon, '0' if int(onu_number) < 10 else '', onu_number, cvlan, phy_address)

def start(bot, update):
  logger.debug('start handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  update.message.reply_text('Menus disponíveis:\n/autorizar\n/sinal\n/reiniciar\n\nAjuda em /help')


def help(bot, update):
  logger.debug('help handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  update.message.reply_text('Menus disponíveis: \n/autorizar\n/sinal\n/reiniciar')

def sinal(bot, update):
  logger.debug('sinal handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    message_list = update.message.text.lower().split(' ')
    if is_onu_id_valid(message_list[1]):
      command_list = ['python3', 'onu_signal_power.py', '-i', '{0}'.format(message_list[1])]
      logger.debug('sinal handler: valid id: command_list: {0}'.format(command_list))
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
      logger.debug('sinal handler: valid id: answer_string: {0}'.format(answer_string))
      if answer_string == 'not found':
        update.message.reply_text('{0} sinal: não existe ONU autorizada com esse ID'.format(message_list[1]))
      elif answer_string == 'off':
        update.message.reply_text('{0}: sem sinal'.format(message_list[1]))
      elif answer_string == 'error':
        update.message.reply_text('{0}: erro não especificado'.format(message_list[1]))
      else:
        update.message.reply_text('{0} sinal: {1}'.format(message_list[1], answer_string))
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).')
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /sinal.')

def reiniciar(bot, update):
  logger.debug('reiniciar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    message_list = update.message.text.lower().split(' ')
    if is_onu_id_valid(message_list[1]):
      command_list = ['python3', 'onu_restart.py', '-i', '{0}'.format(message_list[1])]
      logger.debug('reiniciar handler: valid id: command_list: {0}'.format(command_list))
      answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
      logger.debug('reiniciar handler: valid id: answer_string: {0}'.format(answer_string))
      if answer_string == 'not found':
        update.message.reply_text('{0} reiniciar: sem sinal ou não existe ONU autorizada com esse ID'.format(message_list[1]))
      elif answer_string == 'error':
        update.message.reply_text('{0}: erro não especificado'.format(message_list[1]))
      elif answer_string == 'done':
        update.message.reply_text('{0}: comando enviado com sucesso. A ONU será reiniciada em até 2 minutos.'.format(message_list[1]))
      else:
        update.message.reply_text('{0} reiniciar: resposta desconhecida: {1}'.format(message_list[1], answer_string))
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).')
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /reiniciar.')

def autorizar(bot, update):
  logger.debug('autorizar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    message_list = update.message.text.lower().split(' ')
    if len(message_list) == 1:
      answer_list = subprocess.run(['python3', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(' ')
      logger.debug('autorizar handler: /autorizar: answer_list: {0}'.format(answer_list))
      if '\n' in answer_list:
        answer_list.remove('\n')
      if len(answer_list) is 1:
        if 'None' in answer_list[0]:
          update.message.reply_text('Nenhuma ONU foi encontrada. Envie /autorizar para verificar novamente se há novas ONUs.')
        else:
          update.message.reply_text('Uma ONU foi encontrada: '+answer_list[0]+'\nConfirma serial para autorizar?\nEnvie "/autorizar sim" para autorizar ou /autorizar para verificar novamente se há novas ONUs.')
      else:
        reply_list = []
        for i, answer in enumerate(answer_list):
          reply_list.append(str(i+1)+'. ')
          reply_list.append(answer+'\n')
        update.message.reply_text('ONUs encontradas:\n'+''.join(reply_list)+'Envie o número da ONU que deseja autorizar (ex.: "/autorizar 1") ou /autorizar para verificar novamente se há novas ONUs.')
    elif is_int(message_list[1]):
      if len(message_list) == 3 and is_int(message_list[2]) and int(message_list[2]) > 0 and int(message_list[2]) < 4096:
        answer_string = subprocess.run(['python3', 'authorize_onu.py', '-a', '{0}'.format(message_list[1]), '-v', '{0}'.format(message_list[2])], capture_output=True).stdout.decode('utf-8')
      else:
        answer_string = subprocess.run(['python3', 'authorize_onu.py', '-a', '{0}'.format(message_list[1])], capture_output=True).stdout.decode('utf-8')
      logger.debug('autorizar: int: answer_string: {0}'.format(answer_string))
      if 'OnuDevice' in answer_string:
        update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(answer_string)))
      elif 'ERR' in answer_string:
        update.message.reply_text('A ONU informada não foi encontrada. Envie /autorizar para ver a lista de ONUs disponíveis.')
      elif 'None' in answer_string:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /autorizar para verificar novamente se há novas ONUs.')
    elif 'sim' in message_list[1]:
      if len(message_list) == 3 and is_int(message_list[2]) and int(message_list[2]) > 0 and int(message_list[2]) < 4096:
        answer_string = subprocess.run(['python3', 'authorize_onu.py', '-a', '1', '-v', '{0}'.format(message_list[2])], capture_output=True).stdout.decode('utf-8')
      else:
        answer_string = subprocess.run(['python3', 'authorize_onu.py', '-a', '1'], capture_output=True).stdout.decode('utf-8')
      logger.debug('autorizar: sim: answer_string: {0}'.format(answer_string))
      if 'OnuDevice' in answer_string:
        update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(answer_string)))
      elif 'ERR' in answer_string:
        update.message.reply_text('A ONU não foi encontrada. Envie /autorizar para ver a lista de ONUs disponíveis.')
      elif 'None' in answer_string:
        update.message.reply_text('Nenhuma ONU foi encontrada. Envie /autorizar para verificar novamente.')
    else:
      update.message.reply_text('Para autorizar uma ONU envie /autorizar.')
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /autorizar.')

def usuario(bot, update):
  logger.debug('usuario handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    message_list = update.message.text.lower().split(' ')
    if is_onu_id_valid(message_list[1]):
      answer_string = subprocess.run(['python3', 'user_from_onu.py', '-i', '{0}'.format(message_list[1])], capture_output=True).stdout.decode('utf-8')
      logger.debug('usuario: answer_string: {0}'.format(answer_string))
      if 'None' in answer_string:
        update.message.reply_text('{0} usuario: nenhum usuário associado à ONU foi encontrado.'.format(message_list[1]))
      elif 'ERR' in answer_string:
        update.message.reply_text('{0} usuario: nenhuma ONU encontrada com este ID.'.format(message_list[1]))
      else:
        update.message.reply_text('{0} usuario: {1}'.format(message_list[1], answer_string))
    else:
      update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).')
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /usuario.')

def cto(bot, update):
  logger.debug('cto handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    message_list = update.message.text.lower().split(' ')
    if is_vlan_id_valid(message_list[1]):
      answer_string = subprocess.run(['python3', 'cto_info.py', '-c', '{0}'.format(message_list[1])], capture_output=True).stdout.decode('utf-8')
      logger.debug('cto: answer_string: {0}'.format(answer_string))
    else:
      update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.')
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /cto.')

def cto(bot, update):
  logger.debug('link handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  if is_user_authorized(update.message.from_user.id):
    message_list = update.message.text.lower().split(' ')
    if message_list[1] == 'squid':
      answer_string = subprocess.run(['ssh', '-p', '{0}', '{1}@{2}', '/system', 'script', 'run', '{3}'.format(bot_config.mk_link['ssh']['port'], bot_config.mk_link['ssh']['user'], bot_config.mk_link['ssh']['ip'], bot_config.mk_link['script']['first-link'])], capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
    elif message_list[1] == 'we':
      answer_string = subprocess.run(['ssh', '-p', '{0}', '{1}@{2}', '/system', 'script', 'run', '{3}'.format(bot_config.mk_link['ssh']['port'], bot_config.mk_link['ssh']['user'], bot_config.mk_link['ssh']['ip'], bot_config.mk_link['script']['second-link'])], capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
    elif message_list[1] == 'ambos':
      answer_string = subprocess.run(['ssh', '-p', '{0}', '{1}@{2}', '/system', 'script', 'run', '{3}'.format(bot_config.mk_link['ssh']['port'], bot_config.mk_link['ssh']['user'], bot_config.mk_link['ssh']['ip'], bot_config.mk_link['script']['both-links'])], capture_output=True).stdout.decode('utf-8')
      logger.debug('link: answer_string: {0}'.format(answer_string))
    else:
      update.message.reply_text('Comando inválido. Envie "/link nomedolink" para ativar apenas um link ou "/link ambos" para ativar os dois links.')
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /link.')

def error(bot, update, error):
  logger.warning('Update "%s" caused error "%s"', update, error)
  logger.debug('error handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))

def general(bot, update):
  logger.debug('general handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
  update.message.reply_text('Não entendi. Utilize um dos menus para executar funções. Utilize o menu /help para mais informações.')

def main():
  updater = Updater(bot_config.token)

  dp = updater.dispatcher

  dp.add_handler(CommandHandler("start", start))
  dp.add_handler(CommandHandler("autorizar", autorizar))
  dp.add_handler(CommandHandler("sinal", sinal))
  dp.add_handler(CommandHandler("reiniciar", reiniciar))
  dp.add_handler(CommandHandler("usuario", usuario))
  dp.add_handler(CommandHandler("cto", cto))
  dp.add_handler(CommandHandler("link", link))
  dp.add_handler(CommandHandler("help", help))

  dp.add_handler(MessageHandler(Filters.text, general))

  dp.add_error_handler(error)

  logger.info('Starting...')
  updater.start_polling()

  updater.idle()

if __name__ == '__main__':
  main()