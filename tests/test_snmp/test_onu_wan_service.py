from unittest import TestCase
from unittest.mock import patch

from tasiap.snmp.onu_wan_service import set_wan_service_effective, set_wan_service


class TestOnuWanServiceFunctions(TestCase):

  @patch(target='tasiap.snmp.onu_wan_service.snmpset_hex', side_effect=[None, True])
  @patch(target='tasiap.snmp.onu_wan_service.assure_two_octet_hexstr', return_value='two hex octet')
  @patch(target='tasiap.snmp.onu_wan_service.string_to_hex_octets', return_value='string in hex octet')
  @patch(target='tasiap.snmp.onu_wan_service.int_to_hexoctetstr', return_value='int in hex octet')
  def test_set_wan_service_effective(
      self,
      mock_int_to_hexoctetstr,
      mock_string_to_hex_octets,
      mock_assure_two_octet_hexstr,
      mock_snmpset_hex,
  ):

    hex_string = str(
      '42 47 4D 50 01 00 00 00 00 00 00 8A B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 1F 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 00 {board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 01 00 01 49 4E 54 45 52 4E 45 54 5F 52 5F 56 49 44 5F {cvlan_string_hex} 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 01 00 01 {cvlan_hex} 00 00 01 00 02 64 47 7F CC 00 00 00 20 64 7F 00 01 2D A6 38 15 08 08 08 08 00 '
      '{username_hex} {login_password_hex} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 0F 0F 01 00 FF FF FF FF 00 81 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00'
    ).format(
        board_hex_id=mock_int_to_hexoctetstr.return_value,
        pon_hex_id=mock_int_to_hexoctetstr.return_value,
        onu_hex_number=mock_int_to_hexoctetstr.return_value,
        cvlan_string_hex=mock_string_to_hex_octets.return_value,
        cvlan_hex=mock_assure_two_octet_hexstr.return_value,
        username_hex=mock_string_to_hex_octets.return_value,
        login_password_hex=mock_string_to_hex_octets.return_value
    )

    board_id = '14'
    pon_id = '8'
    onu_number = '99'
    cvlan = '2800'
    username = 'some username'
    login_password = 'some password'

    self.assertFalse(
      expr=set_wan_service_effective(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        cvlan=cvlan,
        username=username,
        login_password=login_password
      )
    )

    mock_snmpset_hex.assert_called_once_with(snmp_oid='1.3.6.1.4.1.5875.91.1.8.1.1.1.13.1', hex_string=hex_string)

    expected_result = {
      'cvlan': cvlan,
      'username': username,
      'password': login_password
    }

    self.assertEqual(
      first=expected_result,
      second=set_wan_service_effective(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        cvlan=cvlan,
        username=username,
        login_password=login_password
      )
    )

  @patch(target='tasiap.snmp.onu_wan_service.set_wan_service_effective', return_value='probably a dict')
  @patch(target='tasiap.snmp.onu_wan_service.get_login_password', return_value='login password')
  @patch(target='tasiap.snmp.onu_wan_service.generate_cvlan', return_value='cvlan')
  @patch(target='tasiap.snmp.onu_wan_service.get_onu_number_from_id', return_value='onu number')
  @patch(target='tasiap.snmp.onu_wan_service.get_pon_id', return_value='pon id')
  @patch(target='tasiap.snmp.onu_wan_service.get_board_id', return_value='board id')
  @patch(target='tasiap.snmp.onu_wan_service.is_onu_id_valid', side_effect=[False, True])
  def test_set_wan_service(
      self,
      mock_is_onu_id_valid,
      mock_get_board_id,
      mock_get_pon_id,
      mock_get_onu_number_from_id,
      mock_generate_cvlan,
      mock_get_login_password,
      mock_set_wan_service_effective
  ):
    onu_id = '1234'
    username = 'some username'

    self.assertFalse(expr=set_wan_service(onu_id=onu_id, username=username))
    mock_is_onu_id_valid.assert_called_once_with(onu_id)

    self.assertEqual(
      first=mock_set_wan_service_effective.return_value,
      second=set_wan_service(onu_id=onu_id, username=username)
    )
    mock_set_wan_service_effective.assert_called_once_with(
      mock_get_board_id.return_value,
      mock_get_pon_id.return_value,
      mock_get_onu_number_from_id.return_value,
      mock_generate_cvlan.return_value,
      username,
      mock_get_login_password.return_value
    )
