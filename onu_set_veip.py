from argparse import ArgumentParser
from subprocess import run

from common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, int_to_hexoctetstr, \
  get_auth_onu_device_id
from logger import get_logger, Log
from config import snmp_config

logger = get_logger(__name__)


def set_veip_effective(board_id, pon_id, onu_number):
  command = 'snmpset -v 2c -c {snmp_community} {snmp_ip} 1.3.6.1.4.1.5875.91.1.8.1.1.1.13.1 x "42 47 4D 50 01 00 00 ' \
            '00 00 00 00 30 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 58 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 01 58 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 {board_hex_id} 00 {pon_hex_id} 00 ' \
            '{onu_hex_number} 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 01 81 00 02 58 FF FF 81 00 FF FF FF FF 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '03 00 03 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00"'.format(snmp_community=snmp_config.community, snmp_ip=snmp_config.ip,
                         board_hex_id=int_to_hexoctetstr(board_id), pon_hex_id=int_to_hexoctetstr(pon_id),
                         onu_hex_number=int_to_hexoctetstr(onu_number))
  run(command, shell=True)
  return {'cvlan': '600'}


@Log(logger)
def set_veip(onu_id=None, auth_onu_device=None):
  if auth_onu_device:
    onu_id = get_auth_onu_device_id(onu_device=auth_onu_device)
  if is_onu_id_valid(onu_id=onu_id):
    board_id = get_board_id(onu_id=onu_id)
    pon_id = get_pon_id(onu_id=onu_id)
    onu_number = get_onu_number_from_id(onu_id=onu_id)
    return set_veip_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number)
  logger.error('set_veip: invalid onu id')
  return None


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU')
  args = parser.parse_args()

  if args.i:
    print(repr(set_veip(args.i)))
    return 0

  print('Informe o ID da ONU.')
  return 1


if __name__ == '__main__':
  main()
