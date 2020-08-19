from subprocess import run

from config import snmp_config
from tasiap.common.string_common import int_to_hexoctetstr


def hex_onu_address(onu_address):
  return '{hex_board_id} 00 {hex_pon_id} 00 {hex_onu_number}'.format(
    hex_board_id=int_to_hexoctetstr(intvalue=onu_address['board_id']),
    hex_pon_id=int_to_hexoctetstr(intvalue=onu_address['pon_id']),
    hex_onu_number=int_to_hexoctetstr(intvalue=onu_address['onu_number'])
  )


def snmpset_hex(snmp_oid, hex_string):
  command = '{snmpset_bin} -v 2c -c {snmp_community} {snmp_ip}:{snmp_port} {snmp_oid} x \'{hex_string}\''.format(
    snmpset_bin=snmp_config.snmpset_bin_path, snmp_community=snmp_config.community,
    snmp_ip=snmp_config.ip, snmp_port=snmp_config.port, snmp_oid=snmp_oid, hex_string=hex_string)
  run(command, shell=True)
  return command
