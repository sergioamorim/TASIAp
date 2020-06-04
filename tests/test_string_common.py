from unittest import TestCase, main

from authorize_onu import AuthOnuDevice, Pon, Board
from common.string_common import get_auth_onu_device_id, sanitize_cto_vlan_name
from common.telnet_common import supply_telnet_connection


class TestStringFunctions(TestCase):

  @supply_telnet_connection
  def test_get_onu_device_id(self, tn=None):
    board_a = Board('14')
    pon_a = Pon('1', board_a, tn=tn)
    onu_a = AuthOnuDevice('1', 'AN5506-04-F1', 'FHTT1177bc38', pon_a)
    onu_a.number = 4

    board_b = Board('12')
    pon_b = Pon('1', board_b, tn=tn)
    onu_b = AuthOnuDevice('1', 'AN5506-04-F1', 'FHTT1177bc38', pon_b)
    onu_b.number = 1

    board_c = Board('14')
    pon_c = Pon('8', board_c, tn=tn)
    onu_c = AuthOnuDevice('1', 'AN5506-04-F1', 'FHTT1177bc38', pon_c)
    onu_c.number = 99

    self.assertEqual(get_auth_onu_device_id(onu_a), '2104')
    self.assertEqual(get_auth_onu_device_id(onu_b), '1101')
    self.assertEqual(get_auth_onu_device_id(onu_c), '2899')

  def test_sanitize_cto_vlan_name(self):
    vlan_a = 'v1101-P12-PON1-ONU01-CTO-PPPOE-MERC-SANTANA'
    vlan_a_sanitized = 'CTO 1101 MERC SANTANA'

    vlan_b = 'v1100-P12-PON1-CLIENTES-FIBRA'

    vlan_c = 'v1135-P12-PON1-ONU35-CTO-PPPOE-MERCADINHO-POPULAR'
    vlan_c_sanitized = 'CTO 1135 MERCADINHO POPULAR'

    vlan_d = 'v4000-PPPOE-TEMPORARIO'

    vlan_e = 'v2806-P14-PON8-ONU06-P2P-PPPOE-TONY'
    vlan_e_sanitized = 'P2P 2806 TONY'

    vlan_f = 'v2115-P14-PON1-ONU15-CTO-PPPOE-SOBS'
    vlan_f_sanitized = 'CTO 2115 SOBS'

    vlan_g = 'v1116-P12-PON5-ONU36-CTO-PPPOE-ACOUGUE-GSS'
    vlan_g_sanitized = 'CTO 1536 (v1116) ACOUGUE GSS'

    vlan_h = 'v1303-P12-PON6-ONU02-CTO-PPPOE-KIDUCHA'
    vlan_h_sanitized = 'CTO 1602 (v1303) KIDUCHA'

    vlan_i = 'REDE-PPPOE-ESCRITORIO'

    self.assertEqual(first=sanitize_cto_vlan_name(vlan_a), second=vlan_a_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_c), second=vlan_c_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_e), second=vlan_e_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_f), second=vlan_f_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_g), second=vlan_g_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_h), second=vlan_h_sanitized)

    self.assertFalse(expr=sanitize_cto_vlan_name(vlan_b))
    self.assertFalse(expr=sanitize_cto_vlan_name(vlan_d))
    self.assertFalse(expr=sanitize_cto_vlan_name(vlan_i))


if __name__ == '__main__':
  main()
