from threading import Thread

from config import bot_config
from tasiap.common.string_common import get_caller_name, is_query_update, get_auth_onu_device_id
from tasiap.find_next_onu_connection import find_onu_connection
from tasiap.onu_signal_power import get_onu_power_signal_by_id


def is_user_authorized(user_id):
  return True if user_id in bot_config.permissions[get_caller_name()] else False


def get_signal(onu_id):
  signal = get_onu_power_signal_by_id(onu_id=onu_id)
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
    onu_id = get_auth_onu_device_id(onu_device=authorized_onu)
    signal = signal_job_caller(context=context, update=update, onu_id=onu_id)
  else:
    signal = get_signal(onu_id)
    if signal == 'sem sinal.':
      signal = signal_job_caller(context=context, update=update, onu_id=onu_id)
  if cvlan and str(cvlan)[2:] == '00' and str(cvlan) != '4000':
    Thread(
      target=find_onu_connection_trigger,
      args=(context.bot, update, onu_id)
    ).start()
  return str(
    'ID: {onu_id}\n'
    '{cvlan_reference}'
    'Serial: {serial}\n'
    'Sinal: {signal}'
  ).format(
    onu_id=onu_id,
    cvlan_reference='CVLAN: {cvlan}\n'.format(cvlan=cvlan) if cvlan else '',
    serial=serial,
    signal=signal
  )


def get_message_from_update(update):
  if is_query_update(update=update):
    return update.callback_query.message
  return update.message


def callback_signal_job(context):
  signal = get_signal(context.job.context['onu_id'])
  context.bot.send_message(
    chat_id=context.job.context['chat_id'],
    text='Sinal: {signal}'.format(signal=signal),
    reply_to_message_id=context.job.context['message_id']
  )
  if context.job.context['chat_id'] != int(bot_config.default_chat):
    context.bot.send_message(
      chat_id=int(bot_config.default_chat),
      text='ONU ID: {onu_id}\nSinal: {signal}'.format(
        onu_id=context.job.context['onu_id'],
        signal=signal
      )
    )


def signal_job_caller(context, update, onu_id):
  message = get_message_from_update(update=update)
  job_context = {
    'chat_id': message.chat.id,
    'onu_id': onu_id,
    'message_id': message.message_id
  }
  context.job_queue.run_once(
    callback=callback_signal_job,
    when=10,
    context=job_context
  )
  return 'ainda em processo de autorização, o sinal será enviado em 10 segundos.'


def find_onu_connection_trigger(bot, update, onu_id):
  message = get_message_from_update(update=update)
  if connection_info := find_onu_connection(onu_id=onu_id):
    message_text = str(
      'Roteador conectado na ONU ID {onu_id}.\n'
      'Usuário: {username}\n'
      'Senha: {password}\n'
      'Status da conexão: {diagnostic}'
    ).format(
      onu_id=onu_id,
      username=connection_info['username'],
      password=connection_info['password'],
      diagnostic=connection_info['diagnostic']
    )
  else:
    message_text = 'Nenhum roteador foi conectado na ONU ID {onu_id}.'.format(
      onu_id=onu_id
    )
  bot.send_message(
    chat_id=message.chat.id,
    text=message_text,
    reply_to_message_id=message.message_id
  )
  if message.chat.id != int(bot_config.default_chat):
    bot.send_message(
      chat_id=int(bot_config.default_chat),
      text=message_text
    )
