from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from config import bot_config
from tasiap.handlers.authorize import authorize
from tasiap.handlers.autorizar import autorizar
from tasiap.handlers.button import button
from tasiap.handlers.cto import cto
from tasiap.handlers.error import error
from tasiap.handlers.general import general
from tasiap.handlers.help_handler import help_handler
from tasiap.handlers.link_handler import link
from tasiap.handlers.login import login
from tasiap.handlers.onuid import onuid
from tasiap.handlers.procurar import procurar
from tasiap.handlers.reiniciar import reiniciar
from tasiap.handlers.sinal import sinal
from tasiap.handlers.start import start
from tasiap.handlers.usuario import usuario
from tasiap.handlers.vlan import vlan
from tasiap.handlers.wifi import wifi
from tasiap.logger import get_logger

logger = get_logger(__name__)


def run():
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
  updater.dispatcher.add_handler(CommandHandler("wifi", wifi))
  updater.dispatcher.add_handler(CommandHandler("link", link))
  updater.dispatcher.add_handler(CallbackQueryHandler(button))
  updater.dispatcher.add_handler(CommandHandler("help", help_handler))
  updater.dispatcher.add_handler(MessageHandler(Filters.text, general))

  updater.dispatcher.add_error_handler(error)

  logger.info('Starting...')
  updater.start_polling()

  updater.idle()
