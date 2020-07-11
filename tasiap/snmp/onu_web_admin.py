from argparse import ArgumentParser

from tasiap.common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, \
  int_to_hexoctetstr, string_to_hex_octects
from config import bot_config
from tasiap.logger import Log, get_logger
from tasiap.snmp.common import snmpset_hex

logger = get_logger(__name__)


def set_web_config_effective(board_id, pon_id, onu_number):
  hex_string = '42 47 4D 50 01 00 00 00 00 00 00 61 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 ' \
               '00 01 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 3C 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 ' \
               '{board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 03 75 73 65 72 61 64 6D 69 6E 00 00 00 00 00 00 00 {password} 00 00 00 01 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 75 73 65 72 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 {password} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 61 64 6D 69 6E 00 00 00 00 00 00 00 00 00 00 00 ' \
               '{password} 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00'.format(board_hex_id=int_to_hexoctetstr(board_id),
                                          pon_hex_id=int_to_hexoctetstr(pon_id),
                                          onu_hex_number=int_to_hexoctetstr(onu_number),
                                          password=string_to_hex_octects(bot_config.default_web_config_password, 32))
  return snmpset_hex(snmp_oid='1.3.6.1.4.1.5875.91.1.22.1.1.1.37.1', hex_string=hex_string)


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
