import unittest

from onu_signal_power import get_signal_power


class TestOutputMethods(unittest.TestCase):

  def test_get_signal_power(self):

    success = "show optic_module slot 12 link 1 onu 1\r\n-----  ONU OPTIC MODULE PAR INFO 10.1.1-----\r\nNAME    " \
                   "      VALUE\tUNIT\r\n---------------------------------------\r\nTYPE         : 20\t(" \
                   "KM)\r\nTEMPERATURE  : 47.00\t('C)\r\nVOLTAGE      :  3.25\t(V)\r\nBIAS CURRENT : 18.78\t(" \
                   "mA)\r\nSEND POWER   :  2.82\t(Dbm)\r\nRECV POWER   : -25.08\t(Dbm)\r\nOLT RECV POWER :  0.00\t(" \
                   "Dbm)\r\nAdmin\\gpononu# ".encode('ascii').decode('ascii')
    error_signal = 'show optic_module slot 14 link 1 onu 7\r\n[ ERR -553 ] onu is in ' \
                   'unactive!\n\rAdmin\\gpononu# '.encode('ascii').decode('ascii')
    error_noauth = 'show optic_module slot 14 link 1 onu 99\r\n[ ERR -506 ] the onu is not ' \
                   'authorized!\n\rAdmin\\gpononu# '.encode('ascii').decode('ascii')
    error_unknown = 'show optic_module slot 14 link 1 onu 99\r\n[ ERR 85 ] simulated error ' \
                    '\n\rAdmin\\gpononu# '.encode('ascii').decode('ascii')
    fail_unknown = 'show optic_module slot 14 link 1 onu 99\r\nsimulated unknown ' \
                   'output\n\rAdmin\\gpononu# '.encode('ascii').decode('ascii')

    self.assertEqual(get_signal_power(success), '-25.08')
    self.assertEqual(get_signal_power(error_signal), 'off')
    self.assertEqual(get_signal_power(error_noauth), 'not found')
    self.assertEqual(get_signal_power(error_unknown), 'error')
    self.assertEqual(get_signal_power(fail_unknown), 'error')


if __name__ == '__main__':
    unittest.main()
