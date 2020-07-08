from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tasiap.onu_authorization import authorize_onu
from tasiap.common.bot_common import is_user_authorized
from tasiap.logger import log_update, get_logger

logger = get_logger(__name__)


def create_keyboard_markup_auth(onu_list):
  keyboard = []
  for onu in onu_list:
    callback_data = "<a=ca><s={0}><b={1}><p={2}>".format(onu.phy_id, onu.pon.board.board_id, onu.pon.pon_id)
    keyboard.append([InlineKeyboardButton(text='Serial: {0} Placa: {1} PON: {2}'.format(onu.phy_id,
                                                                                        onu.pon.board.board_id,
                                                                                        onu.pon.pon_id),
                                          callback_data=callback_data)])
  keyboard.append([InlineKeyboardButton(text='Cancelar', callback_data="<a=aa>")])
  keyboard_markup = InlineKeyboardMarkup(keyboard)
  return keyboard_markup


def autorizar(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      if onu_list := authorize_onu():
        keyboard_markup = create_keyboard_markup_auth(onu_list)
        update.message.reply_text('Confirme os dados da ONU que deseja autorizar:', quote=True,
                                  reply_markup=keyboard_markup)
      else:
        update.message.reply_text(
          'Nenhuma ONU foi encontrada. Envie /autorizar para verificar novamente se há novas ONUs.', quote=True)
    else:
      update.message.reply_text('Para autorizar uma ONU envie /autorizar.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /autorizar.', quote=True)
