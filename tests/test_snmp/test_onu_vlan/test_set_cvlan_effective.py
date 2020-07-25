from unittest import TestCase
from unittest.mock import patch

from tasiap.snmp.onu_vlan import set_cvlan_effective


class TestSetCvlanEffective(TestCase):

  @patch(target='tasiap.snmp.onu_vlan.int_to_hexoctetstr', new=lambda intvalue: 'not relevant')
  @patch(target='tasiap.snmp.onu_vlan.assure_two_octet_hexstr', new=lambda hexstr: 'not relevant')
  @patch(target='tasiap.snmp.onu_vlan.snmpset_hex', new=lambda snmp_oid, hex_string: False)
  def test_none_is_returned_if_snmpset_hex_doesnt_return_positively(self):
    self.assertIsNone(obj=set_cvlan_effective(board_id='12', pon_id='1', onu_number='1', cvlan='1100'))
    self.assertIsNone(obj=set_cvlan_effective(board_id='12', pon_id='1', onu_number='1', cvlan='1100', veip=True))

  @patch(target='tasiap.snmp.onu_vlan.int_to_hexoctetstr')
  @patch(target='tasiap.snmp.onu_vlan.assure_two_octet_hexstr')
  @patch(target='tasiap.snmp.onu_vlan.snmpset_hex', return_value=True)
  def test_veip_oid_and_hex_data_are_used_when_veip_flag_is_set_and_cvlan_is_returned_in_dict(
      self,
      mock_snmpset_hex,
      mock_assure_two_octet_hexstr,
      mock_int_to_hexoctetstr
  ):
    vlan = '1100'

    veip_snmp_oid = '1.3.6.1.4.1.5875.91.1.23.1.1.1.21.1'
    veip_hex_data = str(
      '42 47 4D 50 01 00 00 00 00 00 00 30 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 58 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 58 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 01 00 {board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 01 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 01 81 00 02 58 FF FF 81 00 {cvlan_hex} FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF '
      'FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 03 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00'
    ).format(
      board_hex_id=mock_int_to_hexoctetstr.return_value,
      pon_hex_id=mock_int_to_hexoctetstr.return_value,
      onu_hex_number=mock_int_to_hexoctetstr.return_value,
      cvlan_hex=mock_assure_two_octet_hexstr.return_value
    )

    self.assertEqual(
      first={'cvlan': vlan},
      second=set_cvlan_effective(board_id='12', pon_id='1', onu_number='1', cvlan=vlan, veip=True)
    )
    mock_snmpset_hex.assert_called_once_with(snmp_oid=veip_snmp_oid, hex_string=veip_hex_data)

  @patch(target='tasiap.snmp.onu_vlan.int_to_hexoctetstr')
  @patch(target='tasiap.snmp.onu_vlan.assure_two_octet_hexstr')
  @patch(target='tasiap.snmp.onu_vlan.snmpset_hex', return_value=True)
  def test_ordinary_oid_and_hex_data_are_used_when_veip_flag_is_not_set_and_cvlan_is_returned_in_dict(
      self,
      mock_snmpset_hex,
      mock_assure_two_octet_hexstr,
      mock_int_to_hexoctetstr
  ):
    vlan = '1100'

    ordinary_snmp_oid = '1.3.6.1.4.1.5875.91.1.8.1.1.1.5.1'
    ordinary_hex_string = str(
      '42 47 4D 50 01 00 00 00 00 00 00 00 D7 AC FE 82 BB 34 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A3 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 {board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 01 00 7A 01 01 01 01 01 00 00 01 '
      '00 52 00 00 01 81 00 {cvlan_hex} 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
      '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF 00 00 00 00 '
      '00 00 00 01 00 00 00 00 00 00 00 00 00 00 02 80 00 0F 42 40 00 0F 42 40 00 00 FF FF FF 81 00 FF FF FF 81 00 00 '
      '00 00 00 00 00'
    ).format(
      board_hex_id=mock_int_to_hexoctetstr.return_value,
      pon_hex_id=mock_int_to_hexoctetstr.return_value,
      onu_hex_number=mock_int_to_hexoctetstr.return_value,
      cvlan_hex=mock_assure_two_octet_hexstr.return_value
    )

    self.assertEqual(
      first={'cvlan': vlan},
      second=set_cvlan_effective(board_id='12', pon_id='1', onu_number='1', cvlan=vlan)
    )
    mock_snmpset_hex.assert_called_once_with(snmp_oid=ordinary_snmp_oid, hex_string=ordinary_hex_string)
