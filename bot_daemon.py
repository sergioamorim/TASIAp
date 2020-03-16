from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from config import bot_config
from handlers.authorize import authorize
from handlers.autorizar import autorizar
from handlers.button import button
from handlers.cto import cto
from handlers.error import error
from handlers.general import general
from handlers.help_handler import help_handler
from handlers.link_handler import link
from handlers.login import login
from handlers.onuid import onuid
from handlers.procurar import procurar
from handlers.reiniciar import reiniciar
from handlers.sinal import sinal
from handlers.start import start
from handlers.usuario import usuario
from handlers.vlan import vlan
from logger import get_logger

logger = get_logger(__name__)


def main():
  updater = Updater(bot_config.token, use_context=True)

  updater.dispatcher.add_handler(CommandHandler("start", start))
  updater.dispatcher.add_handler(CommandHandler("autorizar", autorizar))
  updater.dispatcher.add_handler(CommandHandler("authorize", authorize))
  updater.dispatcher.add_handler(CommandHandler("sinal", sinal))
  updater.dispatcher.add_handler(CommandHandler("reiniciar", reiniciar))
  updater.dispatcher.add_handler(CommandHandler("procurar", procurar))
  updater.dispatcher.add_handler(CommandHandler("usuario", usuario))
  updater.dispatcher.add_handler(CommandHandler("login", login))
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
