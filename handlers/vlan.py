from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from common.bot_common import is_user_authorized
from common.string_common import is_onu_id_valid, is_vlan_id_valid
from logger import log_update, get_logger


logger = get_logger(__name__)


def vlan(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if len(context.args) != 2:
      update.message.reply_text('Envie "/vlan 1234 1200" para configurar a ONU de ID 1234 com a CVLAN 1200.',
                                quote=True)
    elif is_onu_id_valid(context.args[0]):
      if (args_1_lower := context.args[1].lower()) == 'cto' or is_vlan_id_valid(context.args[1]):
        keyboard = [[
          InlineKeyboardButton(text='Confirmar',
                               callback_data="<a=v><i={0}><v={1}>".format(context.args[0], args_1_lower)),
          InlineKeyboardButton(text='Cancelar', callback_data="<a=av>")
        ]]
        keyboard_markup = InlineKeyboardMarkup(keyboard)
        text = 'Tem certeza que deseja configurar a ONU de ID *{0}* com a CVLAN *{1}*?'.format(context.args[0],
                                                                                               context.args[1])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, quote=True, reply_markup=keyboard_markup)
      else:
        update.message.reply_text('ID da VLAN inválido. Um ID válido deve estar entre 1 e 4095.', quote=True)
    else:
      update.message.reply_text(
        'ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser '
        'de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).',
        quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o handlers /cto.', quote=True)
