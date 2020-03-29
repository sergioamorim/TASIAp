from re import findall

from common.bot_common import is_user_authorized
from common.string_common import is_onu_id_valid
from config import bot_config
from logger import get_logger, log_update
from manage_router_onu import get_router_onu_info, update_router_onu_config

logger = get_logger(__name__)


def reply_instructions(update):
  message = 'Envie "/wifi 1234 usuario maria" para configurar a ONU roteador de ID 1234 com o usuário maria (a ' \
            'senha dos usuarios user, useradmin a admin será configurada como "{0}").\n\nEnvie "/wifi 1234 rede ' \
            '<@Loja da Maria@> senha <:senha123:>" para configurar a ONU roteador de ID 1234 com o SSID "Loja da ' \
            'Maria" e a senha "senha123".\nÉ possivel enviar somente o nome da rede ou somente a senha a ser ' \
            'configurada seguindo a mesma estrutura.\n\nEnvie "/wifi 1234" para receber as configurações atuais ' \
            'da ONU roteador de ID 1234.'.format(bot_config.default_web_config_password)
  update.message.reply_text(message, quote=True)


def get_web_config_description(result):
  return '{0}'.format(bot_config.default_web_config_password) if result['set_web_config'] else 'erro ao configurar'


def reply_character_limit_exceeded(update, character_limit):
  update.message.reply_text('Limite de caracteres excedido (máximo {0}).'.format(character_limit), quote=True)


def get_ssid_from_args(args):
  args_string = ' '.join(args)
  return findall('<@(.*)@>', args_string)


def get_wifi_password_from_args(args):
  args_string = ' '.join(args)
  return findall('<:(.*):>', args_string)


def wifi(update, context):
  log_update(update, logger)
  if is_user_authorized(update.message.from_user.id):
    if args_len := len(context.args):
      if is_onu_id_valid(context.args[0]):
        onu_id = context.args[0]
        if args_len == 1:
          router_onu_info = get_router_onu_info(onu_id)
          update.message.reply_text('Usuário: {0}\nRede wi-fi: {1}\nSenha do wi-fi: {2}'.format(
            router_onu_info['username'], router_onu_info['ssid'], router_onu_info['wifi_password']), quote=True)
        elif args_len == 2:
          reply_instructions(update)
        elif args_len > 2:
          if context.args[1] == 'usuario':
            username = context.args[2]
            if len(username) > 32:
              reply_character_limit_exceeded(update, 32)
            else:
              result = update_router_onu_config(onu_id, username=username)
              web_config_password = get_web_config_description(result)
              update.message.reply_text('Senha web (user, useradmin, admin): {0}\nUsuário PPPoE: {1}\nSenha PPPoE: '
                                        '{2}'.format(web_config_password, result['set_wan_service']['username'],
                                                     result['set_wan_service']['password']), quote=True)
          elif context.args[1] == 'rede':
            if ssid := get_ssid_from_args(context.args[2]):
              if len(ssid) > 32:
                reply_character_limit_exceeded(update, 32)
              if wifi_password := get_wifi_password_from_args(context.args):
                if len(wifi_password) > 64:
                  reply_character_limit_exceeded(update, 64)
                else:
                  result = update_router_onu_config(onu_id, ssid=ssid, wifi_password=wifi_password)
                  update.message.reply_text('Rede: {0}\nSenha: {1}'.format(result['ssid'],
                                                                           result['wifi_password']), quote=True)
              else:
                result = update_router_onu_config(onu_id, ssid=ssid)
                update.message.reply_text('Rede: {0}\nSenha: {1}'.format(result['ssid'], result['wifi_password']),
                                          quote=True)
            else:
              reply_instructions(update)
          elif context.args[1] == 'senha':
            if wifi_password := get_wifi_password_from_args(context.args):
              if len(wifi_password) > 64:
                reply_character_limit_exceeded(update, 64)
              else:
                result = update_router_onu_config(onu_id, wifi_password=wifi_password)
                update.message.reply_text('Rede: {0}\nSenha: {1}'.format(result['ssid'],
                                                                         result['wifi_password']), quote=True)
            else:
              reply_instructions(update)
          else:
            reply_instructions(update)
      else:
        update.message.reply_text('ID da ONU inválido', quote=True)
    else:
      reply_instructions(update)
  else:
    update.message.reply_text('Você não tem permissão para acessar o menu /authorize.', quote=True)
