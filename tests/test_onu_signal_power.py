import unittest

from onu_signal_power import get_signal_power


class TestOutputMethods(unittest.TestCase):

  def test_get_signal_power(self):

    success = b"show optic_module slot 12 link 1 onu 1\r\n-----  ONU OPTIC MODULE PAR INFO 10.1.1-----\r\nNAME    " \
              b"      VALUE\tUNIT\r\n---------------------------------------\r\nTYPE         : 20\t(" \
              b"KM)\r\nTEMPERATURE  : 47.00\t('C)\r\nVOLTAGE      :  3.25\t(V)\r\nBIAS CURRENT : 18.78\t(" \
              b"mA)\r\nSEND POWER   :  2.82\t(Dbm)\r\nRECV POWER   : -25.08\t(Dbm)\r\nOLT RECV POWER :  0.00\t(" \
              b"Dbm)\r\nAdmin\\gpononu# ".decode('ascii')
    error_signal = b'show optic_module slot 14 link 1 onu 7\r\n[ ERR -553 ] onu is in ' \
                   b'unactive!\n\rAdmin\\gpononu# '.decode('ascii')
    error_noauth = b'show optic_module slot 14 link 1 onu 99\r\n[ ERR -506 ] the onu is not ' \
                   b'authorized!\n\rAdmin\\gpononu# '.decode('ascii')
    error_unknown = b'show optic_module slot 14 link 1 onu 99\r\n[ ERR 85 ] simulated error ' \
                    b'\n\rAdmin\\gpononu# '.decode('ascii')
    fail_unknown = b'show optic_module slot 14 link 1 onu 99\r\nsimulated unknown ' \
                   b'output\n\rAdmin\\gpononu# '.decode('ascii')

    self.assertEqual(get_signal_power(success), '-25.08')
    self.assertEqual(get_signal_power(error_signal), 'off')
    self.assertEqual(get_signal_power(error_noauth), 'not found')
    self.assertEqual(get_signal_power(error_unknown), 'error')
    self.assertEqual(get_signal_power(fail_unknown), 'error')


if __name__ == '__main__':
    unittest.main()
