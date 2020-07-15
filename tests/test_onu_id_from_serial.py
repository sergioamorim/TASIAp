from unittest import TestCase
from unittest.mock import MagicMock

from tasiap.onu_id_from_serial import find_onu_by_serial
from tests.data.onu_id_from_serial_testing_data import test_cases


class TestOnuIdFromSerialFunctions(TestCase):

  def test_find_onu_by_serial(self):
    telnet = MagicMock()

    for test in test_cases:
      telnet.read_until.return_value = test['auth_table']
      for onu in test['onus']:
        self.assertEqual(first=onu['onu_info'], second=find_onu_by_serial(serial=onu['serial'], tn=telnet))
