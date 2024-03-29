from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from tasiap.common.bot_common import is_user_authorized
from tasiap.common.string_common import is_onu_id_valid
from tasiap.logger import log_update, get_logger

logger = get_logger(__name__)


def reiniciar(update, context):
  log_update(update, logger)
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
      update.message.reply_text(
        'ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser '
        'de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).',
        quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /reiniciar.', quote=True)
