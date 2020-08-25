from unittest import TestCase
from unittest.mock import MagicMock, call

from tasiap.onu_id_from_serial import find_onu_by_serial, authorization_table
from tests.data.onu_id_from_serial_testing_data import test_cases


class TestOnuIdFromSerialFunctions(TestCase):

  def test_integrated_find_onu_by_serial(self):
    telnet = MagicMock()

    for test in test_cases:
      telnet.read_until.return_value = test['auth_table']
      for onu in test['onus']:
        self.assertEqual(first=onu['onu_info'], second=find_onu_by_serial(serial=onu['serial'], telnet=telnet))

  def test_authorization_table(self):
    telnet = MagicMock()

    self.assertEqual(
      first=telnet.read_until().decode.return_value,
      second=authorization_table(telnet=telnet),
      msg='Returns the decoded result of the authorization table request'
    )

    self.assertIn(
      member=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'gpononu# '),
        call.write(b'show authorization slot all link all\n'),
        call.read_until(b'gpononu# ')
      ],
      container=telnet.mock_calls,
      msg=str(
        'Requests the authorization table on the gpononu directory from the telnet session passed'
      )
    )
    self.assertIn(
      member=call('ascii'),
      container=telnet.read_until.return_value.decode.mock_calls,
      msg='Decodes the result of the authorization table request from ascii'
    )

    telnet.read_until.return_value = None
    self.assertIsNone(
      obj=authorization_table(telnet=telnet),
      msg='Returns None when the authorization table can not be determined'
    )
