from unittest import TestCase
from unittest.mock import patch, call

from config import snmp_config
from tasiap.snmp.common import snmpset_hex


class TestFunctions(TestCase):

  @patch('tasiap.snmp.common.run')
  def test_snmpset_hex(self, mocking_run):
    test_a_snmp_oid = 'a'
    test_a_hex_string = 'b'

    test_a_command = str(
      '{snmpset_bin} -v 2c -c {snmp_community} {snmp_ip}:{snmp_port} {snmp_oid} x \'{hex_string}\''
      ).format(
        snmpset_bin=snmp_config.snmpset_bin_path, snmp_community=snmp_config.community,
        snmp_ip=snmp_config.ip, snmp_port=snmp_config.port, snmp_oid=test_a_snmp_oid, hex_string=test_a_hex_string
      )

    test_a_calls = [call(test_a_command, shell=True)]

    snmpset_hex(snmp_oid=test_a_snmp_oid, hex_string=test_a_hex_string)

    self.assertEqual(first=test_a_calls, second=mocking_run.call_args_list)
