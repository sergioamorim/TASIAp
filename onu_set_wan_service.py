from argparse import ArgumentParser
from subprocess import run

from common.mysql_common import get_login_password
from common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, \
  int_to_hexoctetstr, string_to_hex_octects, assure_two_octet_hexstr, generate_cvlan
from config import snmp_config
from logger import Log, get_logger

logger = get_logger(__name__)


def set_wan_service_effective(board_id, pon_id, onu_number, cvlan, username, password):
  command = 'snmpset -v 2c -c {0} {1} 1.3.6.1.4.1.5875.91.1.8.1.1.1.13.1 x "42 47 4D 50 01 00 00 00 00 00 00 8A B0 ' \
            'A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 01 00 {2} 00 {3} 00 {4} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 49 4E 54 '\
            '45 52 4E 45 54 5F 52 5F 56 49 44 5F {5} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 {6} 00 00 01 00 02 ' \
            '64 47 7F CC 00 00 00 20 64 7F 00 01 2D A6 38 15 08 08 08 08 00 {7} {8} 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0F 0F 01 00 FF FF FF FF 00 81 00 '\
            'FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"'.format(
             snmp_config.community, snmp_config.ip, int_to_hexoctetstr(board_id), int_to_hexoctetstr(pon_id),
             int_to_hexoctetstr(onu_number), string_to_hex_octects(cvlan, 4),
             assure_two_octet_hexstr(int_to_hexoctetstr(int(cvlan))), string_to_hex_octects(username, 32),
             string_to_hex_octects(password, 32))
  print(command)

  run(command, shell=True)
  return True


@Log(logger)
def set_wan_service(onu_id, username):
  if is_onu_id_valid(onu_id):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number_from_id(onu_id)
    cvlan = generate_cvlan(board_id, pon_id)
    password = get_login_password(username)
    return set_wan_service_effective(board_id, pon_id, onu_number, cvlan, username, password)
  logger.error('set_wan_service: invalid onu id')
  return None


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU')
  parser.add_argument('-u', '--username', dest='u', help='Usuário')
  args = parser.parse_args()

  if args.i and args.u:
    print(set_wan_service(args.i, args.u))
    return 0

  print('Informe o ID da ONU e o usuário.')
  return 1


if __name__ == '__main__':
  main()
