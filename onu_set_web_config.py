from argparse import ArgumentParser
from subprocess import run

from common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, \
  int_to_hexoctetstr, string_to_hex_octects
from config import snmp_config, bot_config
from logger import Log, get_logger

logger = get_logger(__name__)


def set_web_config_effective(board_id, pon_id, onu_number):
  command = 'snmpset -v 2c -c {0} {1} 1.3.6.1.4.1.5875.91.1.22.1.1.1.37.1 x "42 47 4D 50 01 00 00 00 00 00 00 61 B0 ' \
            'A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 00 00 00 00 00 01 00 {2} 00 {3} 00 {4} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '\
            '03 75 73 65 72 61 64 6D 69 6E 00 00 00 00 00 00 00 {5} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 75 73 65 72 00 00 00 00 00 00 00 00 00 00 00 '\
            '00 {5} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 61 64 6D 69 6E 00 00 00 00 00 00 00 00 00 00 00 {5} 00 00 00 02 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"'.format(
             snmp_config.community, snmp_config.ip, int_to_hexoctetstr(board_id), int_to_hexoctetstr(pon_id),
             int_to_hexoctetstr(onu_number), string_to_hex_octects(bot_config.default_web_config_password, 32))
  print(command)

  run(command, shell=True)
  return True


@Log(logger)
def set_web_config(onu_id):
  if is_onu_id_valid(onu_id):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number_from_id(onu_id)
    return set_web_config_effective(board_id, pon_id, onu_number)
  logger.error('set_web_config: invalid onu id')
  return None


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU')
  args = parser.parse_args()

  if args.i:
    print(set_web_config(args.i))
    return 0

  print('Informe o ID da ONU.')
  return 1


if __name__ == '__main__':
  main()
