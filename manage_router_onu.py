from argparse import ArgumentParser
from re import findall

from common.mysql_common import get_login_password
from common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, generate_cvlan
from common.telnet_common import supply_telnet_connection, str_to_telnet
from logger import get_logger, Log

logger = get_logger(__name__)


def encode_login_password(password):
  return ''.join(map(lambda x: chr(x), map(lambda x: 158-ord(x), list(password))))


def get_encoded_login_password(username):
  if login_password := get_login_password(username):
    return encode_login_password(login_password)
  return None


@supply_telnet_connection
def set_router_onu_username_effective(board_id, pon_id, onu_number, cvlan, username, encoded_password, tn=None):
  telnet_command_string = 'set wancfg sl {0} {1} {2} ind 1 mode inter ty r {3} 0 nat en qos dis vlanm tag tvlan ' \
                          'dis 65535 65535 dsp pppoe pro dis {4} key:{5} null auto active en'.format(
                           board_id, pon_id, onu_number, cvlan, username, encoded_password)
  tn.write(str_to_telnet('cd epononu'))
  tn.read_until(b'Admin\\epononu# ', timeout=1)
  tn.write(str_to_telnet('cd qinq'))
  tn.read_until(b'Admin\\epononu\\qinq# ', timeout=1)
  tn.write(str_to_telnet(telnet_command_string))
  if 'failed' not in tn.read_until(b'Admin\\epononu\\qinq# ', timeout=1).decode('ascii'):
    return True
  logger.error('set_router_onu_username_effective: onu s{0} p{1} o{2} not found'.format(board_id, pon_id, onu_number))
  return None


def set_router_onu_username(board_id, pon_id, onu_number, username):
  encoded_password = get_encoded_login_password(username)
  if encoded_password:
    cvlan = generate_cvlan(board_id, pon_id)
    return set_router_onu_username_effective(board_id, pon_id, onu_number, cvlan, username, encoded_password)
  return None


@supply_telnet_connection
def set_router_onu_wifi_effective(board_id, pon_id, onu_number, formatted_ssid, password, tn=None):
  telnet_command_string = 'set wifi_serv_wlan slot {0} link {1} onu {2}  index 1 ssid enable {3} hide disable ' \
                          'authmode wpa2psk encrypt_type aes wpakey {4} interval 0'.format(
                           board_id, pon_id, onu_number, formatted_ssid, password)
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ')
  tn.write(str_to_telnet(telnet_command_string))
  if 'ERR -506' not in tn.read_until(b'Admin\\gpononu# ').decode('ascii'):
    return True
  logger.error('set_router_onu_wifi_effective: onu s{0} p{1} o{2} not found'.format(board_id, pon_id, onu_number))
  return None


@supply_telnet_connection
def get_wifi_data_effective(board_id, pon_id, onu_number, tn=None):
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ')
  tn.write(str_to_telnet('show wifi_serv slot {0} link {1} onu {2}'.format(board_id, pon_id, onu_number)))
  return tn.read_until(b'Admin\\gpononu# ').decode('ascii')


@supply_telnet_connection
def apply_default_wifi_config_effective(board_id, pon_id, onu_number, tn=None):
  telnet_command_string = 'set wifi_serv_cfg slot {0} link {1} onu {2} wifi enable district brazil channel 0'.format(
    board_id, pon_id, onu_number)
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ')
  tn.write(str_to_telnet(telnet_command_string))
  if 'ERR -506' not in tn.read_until(b'Admin\\gpononu# ').decode('ascii'):
    return True
  logger.error('apply_default_wifi_config_effective: onu s{0} p{1} o{2} not found'.format(board_id, pon_id, onu_number))
  return None


@supply_telnet_connection
def get_password(board_id, pon_id, onu_number, tn=None):
  password_pattern = '\\*\\*WPA Share Key:(.*?)\\n'
  wifi_data = get_wifi_data_effective(board_id, pon_id, onu_number, tn=tn)
  if password := findall(password_pattern, wifi_data):
    return password[0].replace('\r', '')
  return None


@supply_telnet_connection
def get_formatted_ssid(board_id, pon_id, onu_number, tn=None):
  ssid_pattern = '\\*\\*SSID:(.*?)\\n'
  wifi_data = get_wifi_data_effective(board_id, pon_id, onu_number, tn=tn)
  if ssid := findall(ssid_pattern, wifi_data):
    return format_ssid(ssid[0].replace('\r', ''))
  return None


def format_ssid(ssid):
  return ''.join([chr(31) if value == 32 else chr(value) for value in ssid.encode('ascii')])


@supply_telnet_connection
def set_router_onu_wifi(board_id, pon_id, onu_number, ssid=None, password=None, tn=None):
  if ssid:
    if apply_default_wifi_config_effective(board_id, pon_id, onu_number, tn=tn):
      formatted_ssid = format_ssid(ssid)
      if not password:
        if not (password := get_password(board_id, pon_id, onu_number, tn=tn)):
          logger.error('set_router_onu_wifi: onu s{0} p{1} o{2} no password'.format(board_id, pon_id, onu_number))
          return None
      return set_router_onu_wifi_effective(board_id, pon_id, onu_number, formatted_ssid, password, tn=tn)
  if password:
    if formatted_ssid := get_formatted_ssid(board_id, pon_id, onu_number, tn=tn):
      return set_router_onu_wifi_effective(board_id, pon_id, onu_number, formatted_ssid, password, tn=tn)
    logger.error('set_router_onu_wifi: onu s{0} p{1} o{2} no ssid'.format(board_id, pon_id, onu_number))
    return None
  return None


@Log(logger)
def update_router_onu_config(onu_id, ssid=None, password=None, username=None):
  if is_onu_id_valid(onu_id):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number_from_id(onu_id)
    if username:
      return set_router_onu_username(board_id, pon_id, onu_number, username)
    if ssid and password:
      return set_router_onu_wifi(board_id, pon_id, onu_number, ssid=ssid, password=password)
    if ssid:
      return set_router_onu_wifi(board_id, pon_id, onu_number, ssid=ssid)
    if password:
      return set_router_onu_wifi(board_id, pon_id, onu_number, password=password)
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
