from argparse import ArgumentParser
from subprocess import run

from common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, \
  int_to_hexoctetstr, string_to_hex_octects
from common.telnet_common import get_ssid, get_wifi_password
from config import snmp_config
from logger import Log, get_logger

logger = get_logger(__name__)


def set_wifi_effective(board_id, pon_id, onu_number, ssid, wifi_password):
  command = 'snmpset -v 2c -c {0} {1} 1.3.6.1.4.1.5875.91.1.23.1.1.1.8.1 x "42 47 4D 50 01 00 00 00 00 00 00 AF B0 A7 '\
            '0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 E1 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 01 E1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 01 00 {2} 00 {3} 00 {4} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 05 00 00 00 04 00 '\
            '14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 {5} 01 00 00 06 00 04 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 {6} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00"'.format(
             snmp_config.community, snmp_config.ip, int_to_hexoctetstr(board_id), int_to_hexoctetstr(pon_id),
             int_to_hexoctetstr(onu_number), string_to_hex_octects(ssid, 32), string_to_hex_octects(wifi_password, 64))
  run(command, shell=True)
  return {'ssid': ssid, 'wifi_password': wifi_password}


@Log(logger)
def set_wifi(onu_id, ssid=None, wifi_password=None):
  if is_onu_id_valid(onu_id) and (ssid or wifi_password):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number_from_id(onu_id)
    if not ssid:
      ssid = get_ssid(board_id, pon_id, onu_number)
    if not wifi_password:
      wifi_password = get_wifi_password(board_id, pon_id, onu_number)
    return set_wifi_effective(board_id, pon_id, onu_number, ssid, wifi_password)
  logger.error('set_wan_service: invalid onu id or no setting parsed')
  return None


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU')
  parser.add_argument('-s', '--ssid', dest='s', help='Nome da rede Wi-Fi', default=None)
  parser.add_argument('-p', '--password', dest='p', help='Senha da rede Wi-Fi', default=None)
  args = parser.parse_args()

  if args.i and args.s and args.p:
    print(set_wifi(args.i, ssid=args.s, wifi_password=args.p))
    return 0
  if args.i and args.s:
    print(set_wifi(args.i, ssid=args.s))
    return 0
  if args.i and args.p:
    print(set_wifi(args.i, wifi_password=args.p))
    return 0

  print('Informe o ID da ONU e a configuração Wi-Fi que deseja alterar.')
  return 1


if __name__ == '__main__':
  main()