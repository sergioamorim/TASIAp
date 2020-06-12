from subprocess import run

from config import snmp_config


def snmpset_hex(snmp_oid, hex_string):
  command = '{snmpset_bin} -v 2c -c {snmp_community} {snmp_ip}:{snmp_port} {snmp_oid} x \'{hex_string}\''.format(
             snmpset_bin=snmp_config.snmpset_bin_path, snmp_community=snmp_config.community,
             snmp_ip=snmp_config.ip, snmp_port=snmp_config.port, snmp_oid=snmp_oid, hex_string=hex_string)
  run(command, shell=True)
  return True
