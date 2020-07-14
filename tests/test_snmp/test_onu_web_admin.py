from unittest import TestCase
from unittest.mock import patch, call

from config import bot_config
from tasiap.snmp.onu_web_admin import set_web_config_effective, set_web_config


class TestOnuWebAdminFunctions(TestCase):

  @patch(target='tasiap.snmp.onu_web_admin.string_to_hex_octets', return_value='string_to_hex_octets result')
  @patch(target='tasiap.snmp.onu_web_admin.int_to_hexoctetstr', return_value='int_to_hexoctetstr result')
  @patch(target='tasiap.snmp.onu_web_admin.snmpset_hex', return_value='snmpset_hex result')
  def test_set_web_config_effective(self, mock_snmpset_hex, mock_int_to_hexoctetstr, mock_string_to_hex_octets):
    bot_config.default_web_config_password = 'fake password'
    board_id = '14'
    pon_id = '8'
    onu_number = '99'

    int_to_hexoctetstr_expected_calls = [
      call(board_id),
      call(pon_id),
      call(onu_number),
    ]

    hex_string = str(
      '42 47 4D 50 01 00 00 00 00 00 00 61 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 3C 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 00 {board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 75 73 65 72 61 64 6D 69 6E 00 00 00 00 00 00 00 {password} 00 00 '
      '00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 75 73 65 '
      '72 00 00 00 00 00 00 00 00 00 00 00 00 {password} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 61 64 6D 69 6E 00 00 00 00 00 00 00 00 00 00 00 {password} 00 '
      '00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    ).format(
      board_hex_id=mock_int_to_hexoctetstr.return_value,
      pon_hex_id=mock_int_to_hexoctetstr.return_value,
      onu_hex_number=mock_int_to_hexoctetstr.return_value,
      password=mock_string_to_hex_octets.return_value
    )

    self.assertEqual(
      first=mock_snmpset_hex.return_value,
      second=set_web_config_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number)
    )

    self.assertEqual(first=int_to_hexoctetstr_expected_calls, second=mock_int_to_hexoctetstr.mock_calls)
    mock_snmpset_hex.assert_called_once_with(snmp_oid='1.3.6.1.4.1.5875.91.1.22.1.1.1.37.1', hex_string=hex_string)
    mock_string_to_hex_octets.assert_called_once_with(bot_config.default_web_config_password, 32)

  @patch(target='tasiap.snmp.onu_web_admin.set_web_config_effective', return_value='probably true')
  @patch(target='tasiap.snmp.onu_web_admin.is_onu_id_valid', side_effect=[False, True])
  @patch(target='tasiap.snmp.onu_web_admin.get_board_id', return_value='board id')
  @patch(target='tasiap.snmp.onu_web_admin.get_pon_id', return_value='pon id')
  @patch(target='tasiap.snmp.onu_web_admin.get_onu_number_from_id', return_value='onu number')
  def test_set_web_config(
      self,
      mock_get_onu_number_from_id,
      mock_get_pon_id,
      mock_get_board_id,
      mock_is_onu_id_valid,
      mock_set_web_config_effective
  ):

    onu_id = 'some onu id'
    self.assertFalse(expr=set_web_config(onu_id=onu_id))
    mock_is_onu_id_valid.assert_called_once_with(onu_id)

    self.assertEqual(first=mock_set_web_config_effective.return_value, second=set_web_config(onu_id=onu_id))

    mock_set_web_config_effective.assert_called_once_with(
      mock_get_board_id.return_value,
      mock_get_pon_id.return_value,
      mock_get_onu_number_from_id.return_value
    )

    mock_get_board_id.assert_called_once_with(onu_id)
    mock_get_pon_id.assert_called_once_with(onu_id)
    mock_get_onu_number_from_id.assert_called_once_with(onu_id)
