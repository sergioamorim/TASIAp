from re import findall

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from authorize_onu import authorize_onu
from common.bot_common import get_onu_info_string
from common.string_common import get_auth_onu_device_id
from config import bot_config
from logger import log_update, get_logger
from onu_restart import restart_onu_by_id
from snmp.onu_set_cvlan import set_cvlan

logger = get_logger(__name__)


def button(update, context):
  log_update(update, logger)
  query = update.callback_query
  action = findall('<a=(.*?)>', query.data)[0]
  if action == 'ca':
    data_pattern = '<s=(.*?)><b=(.*?)><p=(.*?)>'
    regex_result = findall(data_pattern, query.data)
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
    serial = findall('<s=(.*?)>', query.data)[0]
    if authorized_onu := authorize_onu(serial):
      if authorized_onu != 'ERROR':
        onu_id = get_auth_onu_device_id(authorized_onu)
        callback_data = '<a=c><s={0}><i={1}>'.format(authorized_onu.phy_id, onu_id)
        keyboard = [[
          InlineKeyboardButton(text='CTO', callback_data='{0}{1}'.format(callback_data, '<c=cto>')),
          InlineKeyboardButton(text='Cliente', callback_data='{0}{1}'.format(callback_data, '<c=cl>'))
        ]]
        keyboard_markup = InlineKeyboardMarkup(keyboard)
        if query.message.chat.id != int(bot_config.default_chat):
          context.bot.send_message(int(bot_config.default_chat),
                                   '{0} autorizando {1} {2}'.format(query.message.chat.id, onu_id, serial))
        query.edit_message_text('ONU de cliente ou CTO?', reply_markup=keyboard_markup, quote=True)
      else:
        query.edit_message_text('Tente novamente, não foi possivel encontrar a ONU informada agora. Envie /autorizar '
                                'para ver a lista de ONUs disponíveis.', quote=True)
    else:
      query.edit_message_text(
        'Tente novamente, não foi possivel encontrar nenhuma ONU agora. Envie /autorizar para verificar novamente se '
        'há ONUs disponíveis.',
        quote=True)
  elif action == 'c':
    data_pattern = '<s=(.*?)><i=(.*?)><c=(.*?)>'
    regex_result = findall(data_pattern, query.data)
    serial = regex_result[0][0]
    onu_id = regex_result[0][1]
    cvlan = regex_result[0][2]
    if cvlan != 'cto':
      cvlan = None
    if result := set_cvlan(onu_id=onu_id, cvlan=cvlan):
      cvlan_commited = result['cvlan']
    else:
      cvlan_commited = None
    onu_info_string = get_onu_info_string(context, update, onu_id=onu_id, cvlan=cvlan_commited, serial=serial)
    if query.message.chat.id != int(bot_config.default_chat):
      context.bot.send_message(int(bot_config.default_chat),
                               '{0} autorizou\n{1}'.format(query.message.chat.id, onu_info_string))
    query.edit_message_text('ONU autorizada com sucesso.\n{0}'.format(onu_info_string), quote=True)
  elif action == 'aa':
    query.edit_message_text('Autorização cancelada.', quote=True)
  elif action == 'r':
    onu_id = findall('<i=(.*?)>', query.data)[0]
    if restart_result := restart_onu_by_id(onu_id):
      if restart_result == 'done':
        query.edit_message_text('Comando enviado com sucesso. A ONU será reiniciada em até 2 minutos.', quote=True)
      elif restart_result == 'not found':
        query.edit_message_text('Sem sinal ou não existe ONU autorizada com esse ID.', quote=True)
      else:
        query.edit_message_text('Erro não especificado.', quote=True)
    else:
      query.edit_message_text('Não foi possível reiniciar a ONU com o ID informado: ID inválido.', quote=True)
  elif action == 'ar':
    query.edit_message_text('Reinicialização cancelada.', quote=True)
  elif action == 'v':
    data_pattern = '<i=(.*?)><v=(.*?)>'
    regex_result = findall(data_pattern, query.data)
    onu_id = regex_result[0][0]
    cvlan = regex_result[0][1]
    if result := set_cvlan(onu_id=onu_id, cvlan=cvlan):
      cvlan_commited = result['cvlan']
    else:
      cvlan_commited = None
    query.edit_message_text('ONU de ID {0} configurada com sucesso com a CVLAN {1}.'.format(onu_id, cvlan_commited),
                            quote=True)
  elif action == 'av':
    query.edit_message_text('Configuração de CVLAN cancelada.', quote=True)
