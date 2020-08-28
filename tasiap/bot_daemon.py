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
  updater = Updater(token=bot_config.token, use_context=True)

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='start', callback=start)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='autorizar', callback=autorizar)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='authorize', callback=authorize)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='sinal', callback=sinal)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='reiniciar', callback=reiniciar)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='procurar', callback=procurar)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='usuario', callback=usuario)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='login', callback=login)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='onuid', callback=onuid)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='cto', callback=cto)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='vlan', callback=vlan)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='wifi', callback=wifi)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='link', callback=link)
  )

  updater.dispatcher.add_handler(
    handler=CommandHandler(command='help', callback=help_handler)
  )

  updater.dispatcher.add_handler(
    handler=MessageHandler(filters=Filters.text, callback=general)
  )

  updater.dispatcher.add_handler(handler=CallbackQueryHandler(callback=button))
  updater.dispatcher.add_error_handler(callback=error)

  logger.info(msg='Starting...')
  updater.start_polling()

  updater.idle()
