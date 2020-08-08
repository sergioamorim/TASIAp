from unittest import TestCase
from unittest.mock import patch, call

from tasiap.snmp.onu_wifi import set_wifi_effective, set_wifi


class TestOnuWifiFunctions(TestCase):

  @patch(target='tasiap.snmp.onu_wifi.snmpset_hex')
  @patch(target='tasiap.snmp.onu_wifi.string_to_hex_octets')
  @patch(target='tasiap.snmp.onu_wifi.int_to_hexoctetstr')
  def test_set_wifi_effective(self, mock_int_to_hexoctetstr, mock_string_to_hex_octets, mock_snmpset_hex):
    board_id = '12'
    pon_id = '1'
    onu_number = '1'
    ssid = 'network name'
    wifi_password = 'network password'

    snmp_oid = '1.3.6.1.4.1.5875.91.1.23.1.1.1.8.1'
    hex_string = str(
      '42 47 4D 50 01 00 00 00 00 00 00 AF B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 E1 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 E1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 00 {board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 01 00 05 00 00 00 04 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 '
      '{ssid_hex} 01 00 00 06 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 {wifi_password_hex} 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    ).format(
      board_hex_id=mock_int_to_hexoctetstr.return_value,
      pon_hex_id=mock_int_to_hexoctetstr.return_value,
      onu_hex_number=mock_int_to_hexoctetstr.return_value,
      ssid_hex=mock_string_to_hex_octets.return_value,
      wifi_password_hex=mock_string_to_hex_octets.return_value
    )

    mock_snmpset_hex.return_value = False
    self.assertIsNone(
      obj=set_wifi_effective(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        ssid=ssid,
        wifi_password=wifi_password
      ),
      msg='Returns None when snmpset_hex does not respond positively'
    )
    self.assertEqual(
      first=[call(snmp_oid=snmp_oid, hex_string=hex_string)],
      second=mock_snmpset_hex.mock_calls,
      msg='snmpset_hex is called with the wifi snmp oid and hex data format'
    )
    self.assertIn(
      member=[call(board_id), call(pon_id), call(onu_number)],
      container=mock_int_to_hexoctetstr.mock_calls,
      msg=str(
        'The board_id, pon_id and onu_number are transformed into hex octets when put into the hex data sent to '
        'snmpset_hex'
      )
    )
    self.assertIn(
      member=[call(ssid, 32), call(wifi_password, 64)],
      container=mock_string_to_hex_octets.mock_calls,
      msg='The SSID and password are transformed into hex octets with 32 and 64 bytes (respectively) when put into the '
          'hex data sent to snmpset_hex'
    )

    mock_snmpset_hex.return_value = True
    self.assertEqual(
      first={'ssid': ssid, 'wifi_password': wifi_password},
      second=set_wifi_effective(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        ssid=ssid,
        wifi_password=wifi_password
      ),
      msg='Returns a dict with the ssid and the wifi password passed when snmpset_hex responds positively'
    )

  @patch(target='tasiap.snmp.onu_wifi.set_wifi_effective')
  @patch(target='tasiap.snmp.onu_wifi.get_wifi_password')
  @patch(target='tasiap.snmp.onu_wifi.get_ssid')
  @patch(target='tasiap.snmp.onu_wifi.onu_address')
  @patch(target='tasiap.snmp.onu_wifi.is_onu_id_valid')
  def test_set_wifi(
    self,
    mock_is_onu_id_valid,
    mock_onu_address,
    mock_get_ssid,
    mock_get_wifi_password,
    mock_set_wifi_effective
  ):
    onu_id = '1234'
    ssid = 'nw name'
    wifi_password = 'super_secure'
    mock_is_onu_id_valid.return_value = False
    self.assertIsNone(
      obj=set_wifi(onu_id=onu_id, ssid=ssid, wifi_password=wifi_password),
      msg='Returns None when the onu id is not valid'
    )

    mock_is_onu_id_valid.return_value = True
    self.assertIsNone(
      obj=set_wifi(onu_id=onu_id),
      msg='Returns None when neither ssid nor wifi_password are passed'
    )

    self.assertEqual(
      first=mock_set_wifi_effective.return_value,
      second=set_wifi(onu_id=onu_id, ssid=ssid, wifi_password=wifi_password),
      msg='Returns the set_wifi_effective response'
    )
    self.assertIn(
      member=[
        call(
          board_id=mock_onu_address.return_value[''],
          pon_id=mock_onu_address.return_value[''],
          onu_number=mock_onu_address.return_value[''],
          ssid=ssid,
          wifi_password=wifi_password
        )
      ],
      container=mock_set_wifi_effective.mock_calls,
      msg=str(
        'Calls set_wifi_effective with the single values for board_id, pon_id and onu_number - and also the ssid and '
        'wifi password passed'
      )
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_onu_address.mock_calls,
      msg='The onu_address is gathered from the onu_id passed'
    )

    set_wifi(onu_id=onu_id, ssid=ssid)
    self.assertIn(
      member=[
        call(
          board_id=mock_onu_address.return_value[''],
          pon_id=mock_onu_address.return_value[''],
          onu_number=mock_onu_address.return_value[''],
          ssid=ssid,
          wifi_password=mock_get_wifi_password.return_value
        )
      ],
      container=mock_set_wifi_effective.mock_calls,
      msg=str(
        'When no wifi_password is passed, calls set_wifi_effective with the wifi password gathered from the '
        'get_wifi_password function'
      )
    )
    self.assertIn(
      member=[call(onu_address=mock_onu_address.return_value)],
      container=mock_get_wifi_password.mock_calls,
      msg='Calls get_wifi_password with the onu_address gathered from onu_address'
    )

    set_wifi(onu_id=onu_id, wifi_password=wifi_password)
    self.assertIn(
      member=[
        call(
          board_id=mock_onu_address.return_value[''],
          pon_id=mock_onu_address.return_value[''],
          onu_number=mock_onu_address.return_value[''],
          ssid=mock_get_ssid.return_value,
          wifi_password=wifi_password
        )
      ],
      container=mock_set_wifi_effective.mock_calls,
      msg='When no ssid is passed, calls set_wifi_effective with the ssid gathered from the get_ssid function'
    )
    self.assertIn(
      member=call(onu_address=mock_onu_address.return_value),
      container=mock_get_ssid.mock_calls,
      msg='Calls get_ssid with the onu address gathered from onu_address'
    )
