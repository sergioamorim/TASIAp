from unittest import TestCase
from unittest.mock import patch, call, MagicMock

from config import snmp_config
from tasiap.snmp.onu_vlan import can_cvlan_be_set, set_cvlan_effective, treat_cvlan, set_cvlan


class TestOnuVlanFunctions(TestCase):

  @patch(target='tasiap.snmp.onu_vlan.is_onu_id_valid')
  @patch(target='tasiap.snmp.onu_vlan.is_vlan_id_valid')
  def test_can_cvlan_be_set(self, mock_is_vlan_id_valid, mock_is_onu_id_valid):
    mock_is_vlan_id_valid.return_value = False
    mock_is_onu_id_valid.return_value = False
    self.assertFalse(
      expr=can_cvlan_be_set(onu_id='1100', cvlan='0'),
      msg='Returns false when both vlan id and onu id are invalid'
    )

    mock_is_vlan_id_valid.return_value = False
    mock_is_onu_id_valid.return_value = True
    self.assertFalse(
      expr=can_cvlan_be_set(onu_id='1100', cvlan='0'),
      msg='Returns False when the vlan id is invalid, even if the onu id is valid'
    )

    mock_is_vlan_id_valid.return_value = True
    mock_is_onu_id_valid.return_value = False
    self.assertFalse(
      expr=can_cvlan_be_set(onu_id='110a', cvlan='1'),
      msg='Returns False when the onu id is invalid, even if the vlan id is valid'
    )

    mock_is_vlan_id_valid.return_value = True
    mock_is_onu_id_valid.return_value = True
    self.assertTrue(
      expr=can_cvlan_be_set(onu_id='1100', cvlan='1'),
      msg='Returns True when both onu id and cvlan are valid'
    )

  @patch(target='tasiap.snmp.onu_vlan.int_to_hexoctetstr')
  @patch(target='tasiap.snmp.onu_vlan.assure_two_octet_hexstr')
  @patch(target='tasiap.snmp.onu_vlan.snmpset_hex')
  def test_set_cvlan_effective(self, mock_snmpset_hex, mock_assure_two_octet_hexstr, mock_int_to_hexoctetstr):
    vlan = '1100'
    board_id = '12'
    pon_id = '1'
    onu_number = '1'

    mock_snmpset_hex.return_value = True

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
    call_with_veip_snmp_oid_and_hex_data = call(snmp_oid=veip_snmp_oid, hex_string=veip_hex_data)
    self.assertEqual(
      first={'cvlan': vlan},
      second=set_cvlan_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number, cvlan=vlan, veip=True),
      msg='A dict with cvlan is returned and the cvlan value is the vlan passed'
    )
    self.assertEqual(
      first=[call_with_veip_snmp_oid_and_hex_data],  # since calls are cumulative, this needs to be asserted first
      second=mock_snmpset_hex.mock_calls,
      msg='The veip oid and hex data are used when veip lag is set and only one call is made'
    )

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
    call_with_ordinary_snmp_oid_and_hex_data = call(snmp_oid=ordinary_snmp_oid, hex_string=ordinary_hex_string)
    self.assertEqual(
      first={'cvlan': vlan},
      second=set_cvlan_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number, cvlan=vlan)
    )
    self.assertEqual(  # the calls are cumulative, only the second call is actually being evaluated here
      first=[call_with_veip_snmp_oid_and_hex_data, call_with_ordinary_snmp_oid_and_hex_data],
      second=mock_snmpset_hex.mock_calls,
      msg='The ordinary oid and hex data are used when veip lag is set and only one call is made'
    )

    mock_snmpset_hex.return_value = False
    self.assertIsNone(
      obj=set_cvlan_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number, cvlan=vlan),
      msg='None is returned if snmpset_hex doesnt return positively'
    )
    self.assertIsNone(
      obj=set_cvlan_effective(board_id=board_id, pon_id=pon_id, onu_number=onu_number, cvlan=vlan, veip=True),
      msg='None is returned if snmpset_hex doesnt return positively - the veip flag do not affect this behaviour'
    )

  def test_treat_cvlan(self):
    self.assertEqual(
      first='1100',
      second=treat_cvlan(cvlan=None, onu_id='1101'),
      msg=str(
        'vlan is generated from onu_id if none is passed, the generated vlan has the first two digits of the onu id '
        'and the last two digits are zeroes'
      )
    )
    self.assertEqual(
      first='1200',
      second=treat_cvlan(cvlan=None, onu_id='1299'),
      msg=str(
        'vlan is generated from onu_id if none is passed, the generated vlan has the first two digits of the onu id '
        'and the last two digits are zeroes'
      )
    )
    self.assertEqual(
      first='2300',
      second=treat_cvlan(cvlan=None, onu_id='2310'),
      msg=str(
        'vlan is generated from onu_id if none is passed, the generated vlan has the first two digits of the onu id '
        'and the last two digits are zeroes'
      )
    )
    self.assertEqual(
      first='2800',
      second=treat_cvlan(cvlan=None, onu_id='2809'),
      msg=str(
        'vlan is generated from onu_id if none is passed, the generated vlan has the first two digits of the onu id '
        'and the last two digits are zeroes'
      )
    )

    snmp_config.cto_default_cvlan = '4020'
    self.assertEqual(
      first=snmp_config.cto_default_cvlan,
      second=treat_cvlan(cvlan='cto', onu_id='1234'),
      msg="Configured cto vlan is returned when 'cto' is passed as cvlan"
    )

    onu_id = '1234'
    vlan = '1101'
    self.assertEqual(
      first=vlan,
      second=treat_cvlan(cvlan=vlan, onu_id=onu_id),
      msg='Returns the cvlan passed when it has an ordinary value'
    )
    vlan = '1299'
    self.assertEqual(
      first=vlan,
      second=treat_cvlan(cvlan=vlan, onu_id=onu_id),
      msg='Returns the cvlan passed when it has an ordinary value'
    )
    vlan = '1300'
    self.assertEqual(
      first=vlan,
      second=treat_cvlan(cvlan=vlan, onu_id=onu_id),
      msg='Returns the cvlan passed when it has an ordinary value'
    )
    vlan = '2850'
    self.assertEqual(
      first=vlan,
      second=treat_cvlan(cvlan=vlan, onu_id=onu_id),
      msg='Returns the cvlan passed when it has an ordinary value'
    )

  @patch(target='tasiap.snmp.onu_vlan.get_onu_number_from_id')
  @patch(target='tasiap.snmp.onu_vlan.get_pon_id')
  @patch(target='tasiap.snmp.onu_vlan.get_board_id')
  @patch(target='tasiap.snmp.onu_vlan.set_cvlan_effective')
  @patch(target='tasiap.snmp.onu_vlan.get_auth_onu_device_id')
  @patch(target='tasiap.snmp.onu_vlan.find_onu_info')
  @patch(target='tasiap.snmp.onu_vlan.can_cvlan_be_set')
  @patch(target='tasiap.snmp.onu_vlan.treat_cvlan')
  def test_set_cvlan(
      self,
      mock_treat_cvlan,
      mock_can_cvlan_be_set,
      mock_find_onu_info,
      mock_get_auth_onu_device_id,
      mock_set_cvlan_effective,
      mock_get_board_id,
      mock_get_pon_id,
      mock_get_onu_number_from_id
  ):
    auth_onu_device = MagicMock()

    mock_can_cvlan_be_set.return_value = False
    self.assertIsNone(
      obj=set_cvlan(),
      msg='None is returned when nothing is passed'
    )
    self.assertIsNone(
      obj=set_cvlan(onu_id='1234'),
      msg='None is returned when only the onu_id is passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(onu_id='1234', cvlan='1200'),
      msg='None is returned when onu_id and cvlan are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(onu_id='1234', phy_id='ITBS7edac7ed'),
      msg='None is returned when onu_id and ordinary phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(onu_id='1234', phy_id='PACE7edac7ed'),
      msg='None is returned when onu_id and pace phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(onu_id='1234', phy_id='PACE7edac7ed', cvlan='1200'),
      msg='None is returned when onu_id, cvlan and pace phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(onu_id='1234', phy_id='ITBS7edac7ed', cvlan='1200'),
      msg='None is returned when onu_id, cvlan and ordinary phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(phy_id='PACE7edac7ed'),
      msg='None is returned when only pace phy_id is passed - either onu_id or auth_onu_device needs to be passed'
    )
    self.assertIsNone(
      obj=set_cvlan(cvlan='1200'),
      msg='None is returned when only cvlan is passed - either onu_id or auth_onu_device needs to be passed'
    )
    self.assertIsNone(
      obj=set_cvlan(phy_id='ITBS7edac7ed', cvlan='1200'),
      msg=str(
        'None is returned when only ordinary phy_id and cvlan are passed - either onu_id or auth_onu_device needs to '
        'be passed'
      )
    )
    self.assertIsNone(
      obj=set_cvlan(phy_id='PACE7edac7ed', cvlan='1200'),
      msg=str(
        'None is returned when only pace phy_id and cvlan are passed - either onu_id or auth_onu_device needs to '
        'be passed'
      )
    )
    self.assertIsNone(
      obj=set_cvlan(phy_id='ITBS7edac7ed', cvlan='1200'),
      msg=str(
        'None is returned when only ordinary phy_id and cvlan are passed - either onu_id or auth_onu_device needs to '
        'be passed'
      )
    )
    self.assertIsNone(
      obj=set_cvlan(auth_onu_device=auth_onu_device),
      msg='None is returned when only the auth_onu_device is passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(auth_onu_device=auth_onu_device, cvlan='1200'),
      msg='None is returned when auth_onu_device and cvlan are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(auth_onu_device=auth_onu_device, phy_id='ITBS7edac7ed'),
      msg='None is returned when auth_onu_device and ordinary phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(auth_onu_device=auth_onu_device, phy_id='PACE7edac7ed'),
      msg='None is returned when auth_onu_device and pace phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(auth_onu_device=auth_onu_device, phy_id='PACE7edac7ed', cvlan='1200'),
      msg='None is returned when auth_onu_device, cvlan and pace phy_id are passed but cvlan cant be set'
    )
    self.assertIsNone(
      obj=set_cvlan(auth_onu_device=auth_onu_device, phy_id='ITBS7edac7ed', cvlan='1200'),
      msg='None is returned when auth_onu_device, cvlan and ordinary phy_id are passed but cvlan cant be set'
    )

    mock_can_cvlan_be_set.return_value = True
    mock_set_cvlan_effective.reset_mock()
    mock_get_board_id.reset_mock()
    mock_get_pon_id.reset_mock()
    mock_get_onu_number_from_id.reset_mock()
    self.assertEqual(
      first=mock_set_cvlan_effective.return_value,
      second=set_cvlan(auth_onu_device=auth_onu_device, phy_id='ITBS7edac7ed', cvlan='1200'),
      msg=str(
        'The result of set_cvlan_effective is returned when auth_onu_device, cvlan and ordinary phy_id and cvlan can be'
        'set'
      )
    )
    self.assertIn(
      member=call(
        board_id=mock_get_board_id.return_value,
        pon_id=mock_get_pon_id.return_value,
        onu_number=mock_get_onu_number_from_id.return_value,
        cvlan=mock_treat_cvlan.return_value
      ),
      container=mock_set_cvlan_effective.mock_calls,
      msg='The vlan is effectively set after being treated'
    )
    self.assertIn(
      member=call(onu_id=mock_get_auth_onu_device_id.return_value),
      container=mock_get_board_id.mock_calls,
      msg=str(
        'The onu id on which the vlan will effectively be set is gathered with get_auth_onu_device_id if an '
        'auth_onu_device is passed, therefore the board id is got from this onu id'
      )
    )
    self.assertIn(
      member=call(onu_id=mock_get_auth_onu_device_id.return_value),
      container=mock_get_pon_id.mock_calls,
      msg=str(
        'The onu id on which the vlan will effectively be set is gathered with get_auth_onu_device_id if an '
        'auth_onu_device is passed, therefore the pon id is got from this onu id'
      )
    )
    self.assertIn(
      member=call(onu_id=mock_get_auth_onu_device_id.return_value),
      container=mock_get_onu_number_from_id.mock_calls,
      msg=str(
        'The onu id on which the vlan will effectively be set is gathered with get_auth_onu_device_id if an '
        'auth_onu_device is passed, therefore the onu number is got from this onu id'
      )
    )

    mock_set_cvlan_effective.reset_mock()
    mock_get_board_id.reset_mock()
    mock_get_pon_id.reset_mock()
    mock_get_onu_number_from_id.reset_mock()
    mock_find_onu_info.return_value = {'serial': 'ITBS7edac7ed'}
    auth_onu_device.phy_id = 'PACE7edac7ed'
    self.assertEqual(
      first=mock_set_cvlan_effective.return_value,
      second=set_cvlan(auth_onu_device=auth_onu_device, phy_id='ITBS7edac7ed', cvlan='1200'),
      msg=str(
        'The result of set_cvlan_effective is returned when auth_onu_device, cvlan and ordinary phy_id and cvlan can be'
        'set'
      )
    )
    self.assertIn(
      member=call(
        board_id=mock_get_board_id.return_value,
        pon_id=mock_get_pon_id.return_value,
        onu_number=mock_get_onu_number_from_id.return_value,
        cvlan=mock_treat_cvlan.return_value,
        veip=True
      ),
      container=mock_set_cvlan_effective.mock_calls,
      msg=str(
        'The vlan is effectively set after being treated, the veip flag is set if the phy id is from a pace device. '
        'No matter what the phy_id from the find_onu_info function is and neither the phy id passed, when the '
        'auth_onu_device has a phy_id from pace, the flag is set'
      )
    )

    mock_set_cvlan_effective.reset_mock()
    mock_get_board_id.reset_mock()
    mock_get_pon_id.reset_mock()
    mock_get_onu_number_from_id.reset_mock()
    mock_find_onu_info.return_value = {'serial': 'PACE7edac7ed'}
    auth_onu_device.phy_id = None
    self.assertEqual(
      first=mock_set_cvlan_effective.return_value,
      second=set_cvlan(auth_onu_device=auth_onu_device, phy_id='ITBS7edac7ed', cvlan='1200'),
      msg=str(
        'The result of set_cvlan_effective is returned when auth_onu_device, cvlan and ordinary phy_id and cvlan can be'
        'set'
      )
    )
    self.assertIn(
      member=call(
        board_id=mock_get_board_id.return_value,
        pon_id=mock_get_pon_id.return_value,
        onu_number=mock_get_onu_number_from_id.return_value,
        cvlan=mock_treat_cvlan.return_value,
        veip=True
      ),
      container=mock_set_cvlan_effective.mock_calls,
      msg=str(
        'The vlan is effectively set after being treated, the veip flag is set if the phy id is from a pace device. '
        'No matter what the phy_id passed is, when the auth_onu_device has not a phy_id, phy_id gathered from the '
        'find_onu_info function is used to make the evaluation and the veip flag is set accordingly'
      )
    )

    mock_set_cvlan_effective.reset_mock()
    mock_get_board_id.reset_mock()
    mock_get_pon_id.reset_mock()
    mock_get_onu_number_from_id.reset_mock()
    mock_find_onu_info.return_value = None
    auth_onu_device.phy_id = None
    self.assertEqual(
      first=mock_set_cvlan_effective.return_value,
      second=set_cvlan(auth_onu_device=auth_onu_device, phy_id='PACE7edac7ed', cvlan='1200'),
      msg=str(
        'The result of set_cvlan_effective is returned when auth_onu_device, cvlan and ordinary phy_id and cvlan can be'
        'set'
      )
    )
    self.assertIn(
      member=call(
        board_id=mock_get_board_id.return_value,
        pon_id=mock_get_pon_id.return_value,
        onu_number=mock_get_onu_number_from_id.return_value,
        cvlan=mock_treat_cvlan.return_value
      ),
      container=mock_set_cvlan_effective.mock_calls,
      msg=str(
        'The vlan is effectively set after being treated, the veip flag is set if the phy id is from a pace device. '
        'When the auth_onu_device passed has not a phy_id and the find_onu_info function does not return a dict, does '
        'not matter what the phy_id passed is, the flag wont be set'
      )
    )

    mock_set_cvlan_effective.reset_mock()
    mock_get_board_id.reset_mock()
    mock_get_pon_id.reset_mock()
    mock_get_onu_number_from_id.reset_mock()
    mock_find_onu_info.return_value = {'serial': None}
    auth_onu_device.phy_id = None
    self.assertEqual(
      first=mock_set_cvlan_effective.return_value,
      second=set_cvlan(auth_onu_device=auth_onu_device, phy_id='PACE7edac7ed', cvlan='1200'),
      msg=str(
        'The result of set_cvlan_effective is returned when auth_onu_device, cvlan and ordinary phy_id and cvlan can be'
        'set'
      )
    )
    self.assertIn(
      member=call(
        board_id=mock_get_board_id.return_value,
        pon_id=mock_get_pon_id.return_value,
        onu_number=mock_get_onu_number_from_id.return_value,
        cvlan=mock_treat_cvlan.return_value
      ),
      container=mock_set_cvlan_effective.mock_calls,
      msg=str(
        'The vlan is effectively set after being treated, the veip flag is set if the phy id is from a pace device. '
        'No matter what the phy_id passed is, when neither the auth_onu_device has a phy_id or it can be gathered by '
        'the function find_onu_info, the veip flag wont be set'
      )
    )
