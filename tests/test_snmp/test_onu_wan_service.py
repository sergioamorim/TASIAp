from unittest import TestCase
from unittest.mock import patch, call

from tasiap.snmp.onu_wan_service import set_wan_service_effective, set_wan_service, wan_service_hex_string, \
  hex_int_vlan_id


class TestOnuWanServiceFunctions(TestCase):

  @patch(target='tasiap.snmp.onu_wan_service.snmpset_hex')
  @patch(target='tasiap.snmp.onu_wan_service.assure_two_octet_hexstr', return_value='two hex octet')
  @patch(target='tasiap.snmp.onu_wan_service.string_to_hex_octets', return_value='string in hex octet')
  @patch(target='tasiap.snmp.onu_wan_service.hex_onu_address')
  def test_set_wan_service_effective(
    self,
    mock_hex_onu_address,
    mock_string_to_hex_octets,
    mock_assure_two_octet_hexstr,
    mock_snmpset_hex,
  ):
    current_onu_address = {
      'board_id': '14',
      'pon_id': 8,
      'onu_number': '99'
    }

    hex_string = str(
      '42 47 4D 50 01 00 00 00 00 00 00 8A B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 1F 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 00 {hex_onu_address} 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 01 00 01 49 4E 54 45 52 4E 45 54 5F 52 5F 56 49 44 5F {cvlan_string_hex} 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 01 00 01 {cvlan_hex} 00 00 01 00 02 64 47 7F CC 00 00 00 20 64 7F 00 01 2D A6 38 15 08 08 08 08 00 '
      '{hex_username} {hex_login_password} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 0F 0F 01 00 FF FF FF FF 00 81 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00'
    ).format(
      hex_onu_address=mock_hex_onu_address.return_value,
      cvlan_string_hex=mock_string_to_hex_octets.return_value,
      cvlan_hex=mock_assure_two_octet_hexstr.return_value,
      hex_username=mock_string_to_hex_octets.return_value,
      hex_login_password=mock_string_to_hex_octets.return_value
    )

    vlan_id = '2800'
    username = 'some username'
    login_password = 'some password'

    mock_snmpset_hex.return_value = None
    self.assertIsNone(
      obj=set_wan_service_effective(
        current_onu_address=current_onu_address,
        vlan_id=vlan_id,
        username=username,
        login_password=login_password
      ),
      msg='Returns None when snmpset_hex does not have a positive result'
    )
    self.assertIn(
      member=call(
        snmp_oid='1.3.6.1.4.1.5875.91.1.8.1.1.1.13.1',
        hex_string=hex_string
      ),
      container=mock_snmpset_hex.mock_calls,
      msg='Sends the made up hex string with vlan, username and login password to the oid for wan service setting'
    )

    mock_snmpset_hex.return_value = 'something'
    self.assertEqual(
      first={
        'cvlan': vlan_id,
        'username': username,
        'password': login_password
      },
      second=set_wan_service_effective(
        current_onu_address=current_onu_address,
        vlan_id=vlan_id,
        username=username,
        login_password=login_password
      ),
      msg='Returns a dict with the vlan, username and login password passed when snmpset_hex has a positive result'
    )
    self.assertIn(
      member=call(onu_address=current_onu_address),
      container=mock_hex_onu_address.mock_calls,
      msg='Transforms the onu address passed into hex bytes to be put in the hex string to wan service setting'
    )

  @patch(target='tasiap.snmp.onu_wan_service.set_wan_service_effective')
  @patch(target='tasiap.snmp.onu_wan_service.get_login_password')
  @patch(target='tasiap.snmp.onu_wan_service.generate_cvlan')
  @patch(target='tasiap.snmp.onu_wan_service.onu_address')
  @patch(target='tasiap.snmp.onu_wan_service.is_onu_id_valid')
  def test_set_wan_service(
    self,
    mock_is_onu_id_valid,
    mock_onu_address,
    mock_generate_cvlan,
    mock_get_login_password,
    mock_set_wan_service_effective
  ):
    onu_id = '1234'
    username = 'user1'

    mock_is_onu_id_valid.return_value = False
    self.assertIsNone(
      obj=set_wan_service(onu_id=onu_id, username=username),
      msg='Returns None when the onu id passed is invalid'
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_is_onu_id_valid.mock_calls,
      msg='Checks if the onu id passed is valid'
    )

    mock_is_onu_id_valid.return_value = True
    self.assertEqual(
      first=mock_set_wan_service_effective.return_value,
      second=set_wan_service(onu_id=onu_id, username=username),
      msg='Returns the result of set_wan_service_effective if the onu_id passed is valid'
    )
    self.assertIn(
      member=call(
        current_onu_address=mock_onu_address.return_value,
        vlan_id=mock_generate_cvlan.return_value,
        username=username,
        login_password=mock_get_login_password.return_value
      ),
      container=mock_set_wan_service_effective.mock_calls,
      msg=str(
        'Sets the referenced onu with the username passed, the vlan_id generated and the login password found in the '
        'database for the specified username'
      )
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_onu_address.mock_calls,
      msg='Converts the onu id passed into a onu address'
    )
    self.assertIn(
      member=call(username=username),
      container=mock_get_login_password.mock_calls,
      msg='Gather the login password for the username passed from the database'
    )
    self.assertIn(
      member=call(
        board_id=mock_onu_address.return_value[''],
        pon_id=mock_onu_address.return_value['']
      ),
      container=mock_generate_cvlan.mock_calls,
      msg='Generates the vlan_id from the onu address gathered'
    )

  @patch(target='tasiap.snmp.onu_wan_service.hex_onu_address')
  @patch(target='tasiap.snmp.onu_wan_service.string_to_hex_octets')
  @patch(target='tasiap.snmp.onu_wan_service.hex_int_vlan_id')
  def test_wan_service_hex_string(self, mock_hex_int_vlan_id, mock_string_to_hex_octets, mock_hex_onu_address):
    current_onu_address = {
      'board_id': '12',
      'pon_id': '1',
      'onu_number': '1'
    }
    wan_settings = {
      'vlan_id': '1100',
      'username': 'user01',
      'login_password': 'pass123'
    }

    self.assertEqual(
      first=str(
        '42 47 4D 50 01 00 00 00 00 00 00 8A B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 1F '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 {hex_onu_address} 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 01 00 01 49 4E 54 45 52 4E 45 54 5F 52 5F 56 49 44 5F {hex_string_vlan_id} 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 01 00 01 {hex_int_vlan_id} 00 00 01 00 02 64 47 7F CC 00 00 00 20 64 7F 00 01 2D A6 38 15 08 08 08 08 00 '
        '{hex_username} {hex_login_password} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00 00 00 00 00 0F 0F 01 00 FF FF FF FF 00 81 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 '
        '00 00 00 00 00 00 00'
      ).format(
        hex_onu_address=mock_hex_onu_address.return_value,
        hex_string_vlan_id=mock_string_to_hex_octets.return_value,
        hex_int_vlan_id=mock_hex_int_vlan_id.return_value,
        hex_username=mock_string_to_hex_octets.return_value,
        hex_login_password=mock_string_to_hex_octets.return_value
      ),
      second=wan_service_hex_string(current_onu_address, wan_settings),
      msg='Returns a hex string to be used with snmpset_hex on wan_service setting'
    )
    self.assertIn(
      member=call(onu_address=current_onu_address),
      container=mock_hex_onu_address.mock_calls,
      msg='Transforms the onu address passed into hex string to put it into the hex string returned'
    )
    self.assertIn(
      member=call(string=wan_settings['vlan_id'], length=4),
      container=mock_string_to_hex_octets.mock_calls,
      msg=str(
        'Transforms the vlan id as string on the wan settings into a hex string with at least 4 octets to be put into '
        'the hex string returned'
      )
    )
    self.assertIn(
      member=call(vlan_id=wan_settings['vlan_id']),
      container=mock_hex_int_vlan_id.mock_calls,
      msg=str(
        'Transforms the vlan id as int on the wan settings into a hex string with at least 4 octets to be put into the '
        'hex string returned'
      )
    )
    self.assertIn(
      member=call(string=wan_settings['username'], length=32),
      container=mock_string_to_hex_octets.mock_calls,
      msg=str(
        'Transforms the username on the wan settings into a hex string with at least 32 octets to be put into the hex '
        'string returned'
      )
    )
    self.assertIn(
      member=call(string=wan_settings['login_password'], length=32),
      container=mock_string_to_hex_octets.mock_calls,
      msg=str(
        'Transforms the login_password on the wan settings into a hex string with at least 32 octets to be put into '
        'the hex string returned'
      )
    )

  @patch(target='tasiap.snmp.onu_wan_service.assure_two_octet_hexstr')
  @patch(target='tasiap.snmp.onu_wan_service.int_to_hexoctetstr')
  def test_hex_int_vlan_id(self, mock_int_to_hexoctetstr, mock_assure_two_octet_hexstr):
    vlan_id = '1200'
    self.assertEqual(
      first=mock_assure_two_octet_hexstr.return_value,
      second=hex_int_vlan_id(vlan_id=vlan_id),
      msg="Returns the vlan id passed as a two octet hex string from it's int value"
    )
    self.assertIn(
      member=call(hexstr=mock_int_to_hexoctetstr.return_value),
      container=mock_assure_two_octet_hexstr.mock_calls,
      msg='Assures the converted version of the vlan id as int to hex octet string has exactly two octets'
    )
    self.assertIn(
      member=call(intvalue=vlan_id),
      container=mock_int_to_hexoctetstr.mock_calls,
      msg='Converts the vlan id as int to hex octet string'
    )
