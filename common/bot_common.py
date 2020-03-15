from telnetlib import Telnet
from threading import Thread

from common.sqlite_common import update_onu_info
from common.string_common import get_caller_name, is_query_update, get_onu_device_id
from common.telnet_common import connect_su
from config import bot_config, telnet_config
from find_next_onu_connection import find_onu_connection
from onu_signal_power import get_onu_power_signal_by_id


def is_user_authorized(user_id):
  return True if user_id in bot_config.permissions[get_caller_name()] else False


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


def get_onu_info_string(context, update, authorized_onu=None, onu_id=None, cvlan=None, serial=None):
  if authorized_onu:
    serial = authorized_onu.phy_id
    cvlan = authorized_onu.cvlan
    onu_id = get_onu_device_id(authorized_onu)
    signal = signal_job_caller(context, update, onu_id)
  else:
    signal = get_signal(onu_id)
    if signal == 'sem sinal.':
      signal = signal_job_caller(context, update, onu_id)
  if cvlan and cvlan[2:] == '00' and cvlan != '4000':
    Thread(target=find_onu_connection_trigger, args=(context.bot, update, onu_id)).start()
  return 'ID: {0}{1}\nSerial: {2}{3}'.format(onu_id, '\nCVLAN: {0}'.format(cvlan) if cvlan else '', serial,
                                             '\nSinal: {0}'.format(signal))


def get_message_from_update(update):
  if is_query_update(update):
    return update.callback_query.message
  return update.message


def callback_signal_job(context):
  signal = get_signal(context.job.context['onu_id'])
  context.bot.send_message(context.job.context['chat_id'], 'Sinal: {0}'.format(signal),
                           reply_to_message_id=context.job.context['message_id'])
  if context.job.context['chat_id'] != int(bot_config.default_chat):
    context.bot.send_message(int(bot_config.default_chat),
                             'ONU ID: {0}\nSinal: {1}'.format(context.job.context['onu_id'], signal))


def signal_job_caller(context, update, onu_id):
  message = get_message_from_update(update)
  job_context = {'chat_id': message.chat.id, 'onu_id': onu_id, 'message_id': message.message_id}
  context.job_queue.run_once(callback_signal_job, 10, context=job_context)
  return 'ainda em processo de autorização, o sinal será enviado em 10 segundos.'


def find_onu_connection_trigger(bot, update, onu_id):
  message = get_message_from_update(update)
  if connection_info := find_onu_connection(onu_id):
    update_onu_info(int(onu_id), username=connection_info['username'])
    message_text = 'Roteador conectado na ONU ID {0}.\nUsuário: {1}\nSenha: {2}\n' \
                   'Status da conexão: {3}'.format(onu_id, connection_info['username'], connection_info['password'],
                                                   connection_info['diagnostic'])
  else:
    message_text = 'Nenhum roteador foi conectado na ONU ID {0}.'.format(onu_id)
  bot.send_message(message.chat.id, message_text, reply_to_message_id=message.message_id)
  if message.chat.id != int(bot_config.default_chat):
    bot.send_message(int(bot_config.default_chat), message_text)
