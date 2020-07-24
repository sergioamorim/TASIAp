from unittest import TestCase
from unittest.mock import patch

from tasiap.snmp.onu_vlan import can_cvlan_be_set


class TestCanCvlanBeSet(TestCase):

  @patch(target='tasiap.snmp.onu_vlan.is_onu_id_valid')
  @patch(target='tasiap.snmp.onu_vlan.is_vlan_id_valid', new=lambda cvlan: False)
  def test_invalid_vlan_cant_be_set(self, mock_is_onu_id_valid):
    mock_is_onu_id_valid.return_value = True
    self.assertFalse(expr=can_cvlan_be_set(onu_id='1100', cvlan='0'))
    mock_is_onu_id_valid.return_value = False
    self.assertFalse(expr=can_cvlan_be_set(onu_id='1100', cvlan='0'))

  @patch(target='tasiap.snmp.onu_vlan.is_onu_id_valid', new=lambda cvlan: False)
  @patch(target='tasiap.snmp.onu_vlan.is_vlan_id_valid')
  def test_vlan_cant_be_set_on_invalid_onu_id(self, mock_is_vlan_id_valid):
    mock_is_vlan_id_valid.return_value = True
    self.assertFalse(expr=can_cvlan_be_set(onu_id='110a', cvlan='1'))
    mock_is_vlan_id_valid.return_value = False
    self.assertFalse(expr=can_cvlan_be_set(onu_id='110a', cvlan='1'))

  @patch(target='tasiap.snmp.onu_vlan.is_onu_id_valid', new=lambda cvlan: True)
  @patch(target='tasiap.snmp.onu_vlan.is_vlan_id_valid', new=lambda cvlan: True)
  def test_vlan_can_be_set_with_both_valid_onu_id_and_vlan_id(self):
    self.assertTrue(expr=can_cvlan_be_set(onu_id='1100', cvlan='1'))
