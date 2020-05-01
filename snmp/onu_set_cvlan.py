from argparse import ArgumentParser
from subprocess import run

from common.sqlite_common import find_onu_info
from common.string_common import is_onu_id_valid, is_vlan_id_valid, get_auth_onu_device_id, int_to_hexoctetstr, \
  assure_two_octet_hexstr, get_board_id, get_pon_id, get_onu_number_from_id
from config import snmp_config
from logger import Log, get_logger

logger = get_logger(__name__)


def can_cvlan_be_set(onu_id, cvlan):
  return is_vlan_id_valid(cvlan) and onu_id and is_onu_id_valid(onu_id)


def treat_cvlan(cvlan, onu_id):
  if not cvlan:
    return onu_id[:2] + '00'
  elif cvlan == 'cto':
    return snmp_config.cto_default_cvlan
  return cvlan


def set_cvlan_effective(board_id, pon_id, onu_number, cvlan, veip=False):
  if veip:
    command = 'snmpset -v 2c -c {snmp_community} {snmp_ip} 1.3.6.1.4.1.5875.91.1.23.1.1.1.21.1 x "42 47 4D 50 01 00 ' \
              '00 00 00 00 00 30 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 58 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 58 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 {board_hex_id} 00 {pon_hex_id} 00 ' \
              '{onu_hex_number} 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 01 81 00 02 58 FF FF 81 00 {cvlan} FF ' \
              'FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 03 00 03 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
              '00 00 00"'.format(snmp_community=snmp_config.community, snmp_ip=snmp_config.ip,
                                 board_hex_id=int_to_hexoctetstr(board_id), pon_hex_id=int_to_hexoctetstr(pon_id),
                                 onu_hex_number=int_to_hexoctetstr(onu_number),
                                 cvlan=assure_two_octet_hexstr(int_to_hexoctetstr(cvlan)))
  else:
    command = 'snmpset -v 2c -c {snmp_community} {snmp_ip} 1.3.6.1.4.1.5875.91.1.8.1.1.1.5.1 x "42 47 4D 50 01 00 00 ' \
            '00 00 00 00 00 D7 AC FE 82 BB 34 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A3 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 {board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 01 00 7A ' \
            '01 01 01 01 01 00 00 01 00 52 00 00 01 81 00 {cvlan_hex} 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
            '00 00 00 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 02 80 00 0F 42 40 ' \
            '00 0F 42 40 00 00 FF FF FF 81 00 FF FF FF 81 00 00 00 00 00 00 00"'.format(
             snmp_community=snmp_config.community, snmp_ip=snmp_config.ip, board_hex_id=int_to_hexoctetstr(board_id),
             pon_hex_id=int_to_hexoctetstr(pon_id), onu_hex_number=int_to_hexoctetstr(onu_number),
             cvlan_hex=assure_two_octet_hexstr(int_to_hexoctetstr(cvlan)))
  run(command, shell=True)
  return {'cvlan': cvlan}


@Log(logger)
def set_cvlan(auth_onu_device=None, onu_id=None, cvlan=None, phy_id=None):
  if auth_onu_device:
    onu_id = get_auth_onu_device_id(auth_onu_device)
    phy_id = auth_onu_device.phy_id
  if not phy_id:
    if onu_info := find_onu_info(onu_id=onu_id):
      phy_id = onu_info['serial']
  cvlan = treat_cvlan(cvlan, onu_id)
  if can_cvlan_be_set(onu_id, cvlan):
    board_id = get_board_id(onu_id=onu_id)
    pon_id = get_pon_id(onu_id=onu_id)
    onu_number = get_onu_number_from_id(onu_id=onu_id)
    if phy_id and phy_id[:4] == 'PACE':
      return set_cvlan_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number, cvlan=cvlan, veip=True)
    else:
      return set_cvlan_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number, cvlan=cvlan)
  return None


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU em que a VLAN vai ser configurada', default=None)
  parser.add_argument('-c', '--cvlan', dest='c', help='CVLAN a ser configurada na ONU', default=None)
  args = parser.parse_args()

  print(set_cvlan(onu_id=args.i, cvlan=args.c))

  return 0


if __name__ == '__main__':
  main()
