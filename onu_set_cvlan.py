from argparse import ArgumentParser
from subprocess import run

from common.string_common import is_onu_id_valid, is_vlan_id_valid, get_auth_onu_device_id
from config import snmp_config
from logger import Log, get_logger

logger = get_logger(__name__)


def format_strhexoctet(strhexoctet):
  return strhexoctet.zfill(2).upper()


def hexstr_to_hexoctetstr(hexstr):
  if len(hexstr) > 2:
    return hexstr_to_hexoctetstr(hexstr[:-2]) + ' ' + format_strhexoctet(hexstr[-2:])
  return format_strhexoctet(hexstr[-2:])


def int_to_hexoctetstr(intvalue):
  return hexstr_to_hexoctetstr(format(intvalue, 'x'))


def assure_two_octet_hexstr(hexstr):
  if len(hexstr) == 2:
    return '00 ' + hexstr
  return hexstr


def can_cvlan_be_set(onu_id, cvlan):
  return is_vlan_id_valid(cvlan) and onu_id and is_onu_id_valid(onu_id)


def treat_cvlan(cvlan, onu_id):
  if not cvlan:
    return int(onu_id[:2] + '00')
  elif cvlan == 'cto':
    return snmp_config.cto_default_cvlan
  return cvlan


@Log(logger)
def set_cvlan(auth_onu_device=None, onu_id=None, cvlan=None):
  if auth_onu_device:
    onu_id = get_auth_onu_device_id(auth_onu_device)
  cvlan = treat_cvlan(cvlan, onu_id)
  if not can_cvlan_be_set(onu_id, cvlan):
    return None
  board_id = 12 if onu_id[:1] == '1' else 14
  pon_id = int(onu_id[1:2])
  onu_number = int(onu_id[2:])
  command = 'snmpset -v 2c -c {0} {1} 1.3.6.1.4.1.5875.91.1.8.1.1.1.5.1 x "42 47 4D 50 01 00 00 00 00 00 00 00 D7 ' \
            'AC FE 82 BB 34 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A3 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 {2} 00 {3} 00 {4} 00 01 00 7A 01 01 01 01 01 00 00 01 00 52 00 00 01 81 00 {5} 00 ' \
            '00 81 00 FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 01 00 00 ' \
            '00 00 00 00 00 00 00 00 02 80 00 0F 42 40 00 0F 42 40 00 00 FF FF FF 81 00 FF FF FF 81 00 00 00 00 00 ' \
            '00 00"'.format(snmp_config.community, snmp_config.ip, int_to_hexoctetstr(board_id),
                            int_to_hexoctetstr(pon_id), int_to_hexoctetstr(onu_number),
                            assure_two_octet_hexstr(int_to_hexoctetstr(int(cvlan))))
  run(command, shell=True)
  cvlan_set = {'onu_id': onu_id, 'cvlan': str(cvlan)}
  return cvlan_set


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU em que a VLAN vai ser configurada', default=None)
  parser.add_argument('-c', '--cvlan', dest='c', help='CVLAN a ser configurada na ONU', default=None)
  args = parser.parse_args()

  print(set_cvlan(onu_id=args.i, cvlan=args.c))

  return 0


if __name__ == '__main__':
  main()
