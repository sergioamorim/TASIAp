import subprocess

from bot_daemon import logger, is_user_authorized, create_keyboard_markup_auth
from logger import log_update


def autorizar(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if not len(context.args):
      answer_list = subprocess.run(['python3.8', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(
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
