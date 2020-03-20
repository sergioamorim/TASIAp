import unittest

from onu_id_from_username import get_onu_number


class TestOutputMethods(unittest.TestCase):

  def test_get_onu_number(self):

    success = b'show pon_mac slot 12 link 1 lookup E4BEED22E4F3\r\n-----  PON MAC ADDRESS, ITEM=208 ' \
              b'-----\n\r203\tE4:BE:ED:22:E4:F3\t Vid:1119\t OnuId:19\n\rAdmin\\gponline# '.decode('ascii')
    error = b'show pon_mac slot 12 link 1 lookup A1AAAA11A1A1\r\n-----  PON MAC ADDRESS, ITEM=208 ' \
            b'-----\n\rAdmin\\gponline# '.decode('ascii')

    self.assertEqual(get_onu_number(success), '19')
    self.assertEqual(get_onu_number(error), None)


if __name__ == '__main__':
    unittest.main()
