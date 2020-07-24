from unittest import TestCase

from config import snmp_config
from tasiap.snmp.onu_vlan import treat_cvlan


class TestTreatCvlan(TestCase):

  def test_vlan_is_generated_from_onu_id_if_none_is_passed(self):
    vlan = None
    self.assertEqual(first='1100', second=treat_cvlan(cvlan=vlan, onu_id='1101'))
    self.assertEqual(first='1200', second=treat_cvlan(cvlan=vlan, onu_id='1299'))
    self.assertEqual(first='2300', second=treat_cvlan(cvlan=vlan, onu_id='2310'))
    self.assertEqual(first='2800', second=treat_cvlan(cvlan=vlan, onu_id='2809'))

  def test_configured_cto_vlan_is_returned_when_cto_is_passed_as_cvlan(self):
    snmp_config.cto_default_cvlan = '4020'
    self.assertEqual(first=snmp_config.cto_default_cvlan, second=treat_cvlan(cvlan='cto', onu_id='1234'))

  def test_ordinary_vlan_is_just_returned(self):
    onu_id = '1234'
    vlan = '1101'
    self.assertEqual(first=vlan, second=treat_cvlan(cvlan=vlan, onu_id=onu_id))
    vlan = '1299'
    self.assertEqual(first=vlan, second=treat_cvlan(cvlan=vlan, onu_id=onu_id))
    vlan = '1300'
    self.assertEqual(first=vlan, second=treat_cvlan(cvlan=vlan, onu_id=onu_id))
    vlan = '2850'
    self.assertEqual(first=vlan, second=treat_cvlan(cvlan=vlan, onu_id=onu_id))
