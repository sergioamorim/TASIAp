from re import findall
from subprocess import run

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot_daemon import logger
from common.bot_common import is_user_authorized
from logger import log_update


def create_keyboard_markup_auth(onu_serials_list):
  keyboard = []
  for onu_serial in onu_serials_list:
    onu_serial_regex_list = findall('(.*)_(.*)_(.*)', onu_serial)
    board = onu_serial_regex_list[0][0]
    pon = onu_serial_regex_list[0][1]
    serial = onu_serial_regex_list[0][2]
    callback_data = "<a=ca><s={0}><b={1}><p={2}>".format(serial, board, pon)
    keyboard.append([InlineKeyboardButton(text='Serial: {0} Placa: {1} PON: {2}'.format(serial, board, pon),
                                          callback_data=callback_data)])
  keyboard.append([InlineKeyboardButton(text='Cancelar', callback_data="<a=aa>")])
  keyboard_markup = InlineKeyboardMarkup(keyboard)
  return keyboard_markup


def autorizar(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      answer_list = run(['python3.8', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(
        ' ')
      logger.debug('autorizar handler: /autorizar: answer_list: {0}'.format(answer_list))
      if '\n' in answer_list:
        answer_list.remove('\n')
      if len(answer_list) == 1 and 'None' in answer_list[0]:
        update.message.reply_text(
          'Nenhuma ONU foi encontrada. Envie /autorizar para verificar novamente se há novas ONUs.', quote=True)
      else:
        keyboard_markup = create_keyboard_markup_auth(answer_list)
        update.message.reply_text('Confirme os dados da ONU que deseja autorizar:', quote=True,
                                  reply_markup=keyboard_markup)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /autorizar.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /autorizar.', quote=True)
