from unittest import TestCase, main

from authorize_onu import AuthOnuDevice, Pon, Board
from common.string_common import get_auth_onu_device_id
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


if __name__ == '__main__':
  main()
