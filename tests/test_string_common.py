from unittest import TestCase, main

from authorize_onu import OnuDevice, Pon, Board
from common.string_common import get_onu_device_id


class TestStringFunctions(TestCase):

  def test_get_onu_device_id(self):
    board_a = Board('14')
    pon_a = Pon('1', board_a)
    onu_a = OnuDevice('1', 'AN5506-04-F1', 'FHTT1177bc38', pon_a)
    onu_a.number = 4

    self.assertEqual(get_onu_device_id(onu_a), '2104')

    board_b = Board('12')
    pon_b = Pon('1', board_b)
    onu_b = OnuDevice('1', 'AN5506-04-F1', 'FHTT1177bc38', pon_b)
    onu_b.number = 1

    self.assertEqual(get_onu_device_id(onu_b), '1101')

    board_c = Board('14')
    pon_c = Pon('8', board_c)
    onu_c = OnuDevice('1', 'AN5506-04-F1', 'FHTT1177bc38', pon_c)
    onu_c.number = 99

    self.assertEqual(get_onu_device_id(onu_c), '2899')


if __name__ == '__main__':
  main()