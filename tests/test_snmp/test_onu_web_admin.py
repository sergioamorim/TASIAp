from unittest import TestCase
from unittest.mock import patch, call

from config import bot_config
from tasiap.snmp.onu_web_admin import set_web_config_effective, set_web_config, web_config_hex_string


class TestOnuWebAdminFunctions(TestCase):

  @patch(target='tasiap.snmp.onu_web_admin.hex_onu_address')
  @patch(target='tasiap.snmp.onu_web_admin.string_to_hex_octets', return_value='string_to_hex_octets result')
  @patch(target='tasiap.snmp.onu_web_admin.snmpset_hex', return_value='snmpset_hex result')
  def test_set_web_config_effective(self, mock_snmpset_hex, mock_string_to_hex_octets, mock_hex_onu_address):
    current_onu_address = {
      'board_id': '14',
      'pon_id': '8',
      'onu_number': '99'
    }
    web_password = 'my_pass123'

    hex_string = str(
      '42 47 4D 50 01 00 00 00 00 00 00 61 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 3C 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 00 {hex_onu_address} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 03 75 73 65 72 61 64 6D 69 6E 00 00 00 00 00 00 00 {hex_web_password} 00 00 00 01 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 75 73 65 72 00 00 00 00 00 00 00 00 '
      '00 00 00 00 {hex_web_password} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 61 64 6D 69 6E 00 00 00 00 00 00 00 00 00 00 00 {hex_web_password} 00 00 00 02 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    ).format(
      hex_onu_address=mock_hex_onu_address.return_value,
      hex_web_password=mock_string_to_hex_octets.return_value
    )

    self.assertEqual(
      first=mock_snmpset_hex.return_value,
      second=set_web_config_effective(current_onu_address=current_onu_address, web_password=web_password),
      msg='Returns the result of the snmpset_hex'
    )

    self.assertIn(
      member=call(onu_address=current_onu_address),
      container=mock_hex_onu_address.mock_calls,
      msg='Transforms the onu address passed into hex bytes to use with snmpset_hex'
    )
    self.assertEqual(
      first=[call(snmp_oid='1.3.6.1.4.1.5875.91.1.22.1.1.1.37.1', hex_string=hex_string)],
      second=mock_snmpset_hex.mock_calls,
      msg='Sends the hex string created to the web config oid via snmpset_hex'
    )
    self.assertEqual(
      first=[call(string=web_password, length=32)],
      second=mock_string_to_hex_octets.mock_calls,
      msg='Includes the web password passed as a 32 bytes hex string in the string sent to snmpset_hex'
    )

  @patch(target='tasiap.snmp.onu_web_admin.set_web_config_effective')
  @patch(target='tasiap.snmp.onu_web_admin.is_onu_id_valid')
  @patch(target='tasiap.snmp.onu_web_admin.onu_address')
  def test_set_web_config(
    self,
    mock_onu_address,
    mock_is_onu_id_valid,
    mock_set_web_config_effective
  ):
    bot_config.default_web_config_password = 'pass_substitute'
    onu_id = 'some onu id'

    mock_is_onu_id_valid.return_value = False
    self.assertIsNone(
      obj=set_web_config(onu_id=onu_id),
      msg='Returns None when the onu id passed is invalid'
    )
    self.assertEqual(
      first=[call(onu_id=onu_id)],
      second=mock_is_onu_id_valid.mock_calls,
      msg='Checks if the onu id passed is valid'
    )

    mock_is_onu_id_valid.return_value = True
    self.assertEqual(
      first=mock_set_web_config_effective.return_value,
      second=set_web_config(onu_id=onu_id),
      msg='Returns the result of the effective setting when the onu id passed is valid'
    )
    self.assertIn(
      member=call(
        current_onu_address=mock_onu_address.return_value,
        web_password=bot_config.default_web_config_password
      ),
      container=mock_set_web_config_effective.mock_calls,
      msg='Sets the web password of the onu on the onu address passed to the default web password in the bot_config'
    )
    self.assertEqual(
      first=[call(onu_id=onu_id)],
      second=mock_onu_address.mock_calls,
      msg='Gather the onu address from the onu id passed'
    )

  @patch(target='tasiap.snmp.onu_web_admin.string_to_hex_octets')
  @patch(target='tasiap.snmp.onu_web_admin.hex_onu_address')
  def test_web_config_hex_string(self, mock_hex_onu_address, mock_string_to_hex_octets):
    current_onu_address = 'onu address dict'
    web_password = 'passwd1234'
    self.assertEqual(
      first=str(
        '42 47 4D 50 01 00 00 00 00 00 00 61 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 3C '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 {hex_onu_address} 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 03 75 73 65 72 61 64 6D 69 6E 00 00 00 00 00 00 00 {hex_web_password} 00 00 00 01 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 75 73 65 72 00 '
        '00 00 00 00 00 00 00 00 00 00 00 {hex_web_password} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 61 64 6D 69 6E 00 00 00 00 00 00 00 00 00 00 00 '
        '{hex_web_password} 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00'
      ).format(
        hex_onu_address=mock_hex_onu_address.return_value,
        hex_web_password=mock_string_to_hex_octets.return_value
      ),
      second=web_config_hex_string(current_onu_address=current_onu_address, web_password=web_password),
      msg='Returns a web config hex string with the onu address and web password passed'
    )
    self.assertIn(
      member=call(onu_address=current_onu_address),
      container=mock_hex_onu_address.mock_calls,
      msg='Transforms the onu address passed into hex bytes to be put in the web config hex string'
    )
    self.assertIn(
      member=call(string=web_password, length=32),
      container=mock_string_to_hex_octets.mock_calls,
      msg='The web password passed is transformed into 32 hex bytes to be put in the web config hex string'
    )
