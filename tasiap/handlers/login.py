from tasiap.common.bot_common import is_user_authorized
from tasiap.logger import get_logger, log_update
from tasiap.login_info import find_login_info

logger = get_logger(__name__)


def login(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if len(context.args) != 1:
      update.message.reply_text('Envie "/login maria" para receber informações sobre o usuário maria.', quote=True)
    else:
      if login_info := find_login_info(context.args[0]):
        update.message.reply_text(login_info, quote=True)
      else:
        update.message.reply_text('Usuário inexistente.', quote=True)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /login.', quote=True)
