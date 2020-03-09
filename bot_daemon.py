#!/usr/bin/env python3.8
# coding=utf-8

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import re
import bot_config

from handlers.authorize import authorize
from handlers.autorizar import autorizar
from handlers.button import button
from handlers.cto import cto
from handlers.error import error
from handlers.general import general
from handlers.help_handler import help_handler
from handlers.link_handler import link
from handlers.onuid import onuid
from handlers.procurar import procurar
from handlers.reiniciar import reiniciar
from handlers.start import start
from handlers.usuario import usuario
from handlers.vlan import vlan
from logger import logger
from onu_signal_power import get_onu_power_signal_by_id
from telnetlib import Telnet
import telnet_config
from telnet_common import connect_su
from string_common import get_onu_id_from_repr, get_caller_name
from find_next_onu_connection import find_onu_connection
from threading import Thread
from sqlite_common import update_onu_info
from handlers.sinal import sinal


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


def get_message_from_update(update):
  try:
    update.message.chat
    return update.message
  except:
    return update.callback_query.message


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


def get_onu_info_string(context, update, onu_repr=None, onu_id=None, cvlan=None, serial=None):
  if onu_repr:
    onu_repr_pattern = "([0-9A-Z]{4}[0-9A-Fa-f]{8})',pon='<Pon\(pon_id='[0-9]',board='<Board\(board_id='[0-9]{" \
                       "2}'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='[0-9]+'," \
                       "cvlan='(N?o?n?e?[0-9]{0,4}) "
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
  return 'ID: {0}{1}\nSerial: {2}{3}'.format(onu_id, '\nCVLAN: {0}'.format(cvlan) if cvlan else '', serial,
                                             '\nSinal: {0}'.format(signal))


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
  updater.dispatcher.add_handler(CommandHandler("help", help_handler))
  updater.dispatcher.add_handler(MessageHandler(Filters.text, general))

  updater.dispatcher.add_error_handler(error)

  logger.info('Starting...')
  updater.start_polling()

  updater.idle()


if __name__ == '__main__':
  main()
