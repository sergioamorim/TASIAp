from unittest import TestCase
from unittest.mock import patch, call

from config import snmp_config
from tasiap.snmp.common import snmpset_hex, hex_onu_address


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

  @patch(target='tasiap.snmp.common.int_to_hexoctetstr')
  def test_hex_onu_address(self, mock_int_to_hexoctetstr):
    onu_address = {
      'board_id': '12',
      'pon_id': '1',
      'onu_number': '1'
    }
    self.assertEqual(
      first='{hex_board_id} 00 {hex_pon_id} 00 {hex_onu_number}'.format(
        hex_board_id=mock_int_to_hexoctetstr.return_value,
        hex_pon_id=mock_int_to_hexoctetstr.return_value,
        hex_onu_number=mock_int_to_hexoctetstr.return_value
      ),
      second=hex_onu_address(onu_address=onu_address),
      msg=str(
        'Returns a string with the onu address written in hexadecimal with zero octets between the board_id and the '
        'pon_id and between the pon_id and the onu_number'
      )
    )
    self.assertIn(
      member=[
        call(intvalue=onu_address['board_id']),
        call(intvalue=onu_address['pon_id']),
        call(intvalue=onu_address['onu_number'])
      ],
      container=mock_int_to_hexoctetstr.mock_calls,
      msg='Gather the hex values for board_id, pon_id and onu_number from the int_to_hexoctetstr function'
    )
