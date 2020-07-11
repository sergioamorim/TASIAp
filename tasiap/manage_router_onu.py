from argparse import ArgumentParser

from tasiap.common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id
from tasiap.common.telnet_common import get_wifi_password, get_ssid, supply_telnet_connection
from tasiap.logger import get_logger, Log
from tasiap.snmp.onu_wan_service import set_wan_service
from tasiap.snmp.onu_web_admin import set_web_config
from tasiap.snmp.onu_wifi import set_wifi
from tasiap.user_from_onu import find_user_by_onu

logger = get_logger(__name__)


@supply_telnet_connection
def get_router_onu_info(onu_id, tn=None):
  if is_onu_id_valid(onu_id):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number_from_id(onu_id)
    ssid = get_ssid(board_id, pon_id, onu_number, tn=tn)
    wifi_password = get_wifi_password(board_id, pon_id, onu_number, tn=tn)
    username = find_user_by_onu(onu_id)
    return {'onu_id': onu_id, 'ssid': ssid, 'wifi_password': wifi_password, 'username': username}
  logger.error('get_router_onu_info: onu id is invalid')
  return None


@Log(logger)
def update_router_onu_config(onu_id, ssid=None, wifi_password=None, username=None):
  if is_onu_id_valid(onu_id):
    if username:
      return {'set_web_config': set_web_config(onu_id), 'set_wan_service': set_wan_service(onu_id, username)}
    if ssid and wifi_password:
      return set_wifi(onu_id, ssid=ssid, wifi_password=wifi_password)
    if ssid:
      return set_wifi(onu_id, ssid=ssid)
    if wifi_password:
      return set_wifi(onu_id, wifi_password=wifi_password)
  logger.error('update_router_onu_config: onu id is invalid')
  return None


def main():

  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser configurada')
  parser.add_argument('-s', '--ssid', dest='s', help='SSID a ser configurado', default=None)
  parser.add_argument('-p', '--password', dest='p', help='Senha do Wi-Fi a ser configurada', default=None)
  parser.add_argument('-u', '--username', dest='u', help='Usuário a ser configurado', default=None)
  args = parser.parse_args()

  if manage_result := update_router_onu_config(args.i, ssid=args.s, password=args.p, username=args.u):
    print(repr(manage_result))
    return 0

  return 1


if __name__ == '__main__':
  main()
