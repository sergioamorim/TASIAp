import unittest
from unittest.mock import patch, MagicMock, call

from tasiap.onu_signal_power import get_signal_power, get_onu_power_signal_by_id
from tests.data.telnet_testing_data import test_params, test_data
from tests.telnet_testing_environment import TelnetTestingEnvironment


def translate_onu_id(board_id, pon_id, onu_number):
  board_reference = '1' if board_id == '12' else '2'
  onu_reference = '0{onu_number}'.format(
    onu_number=onu_number
  ) if int(onu_number) < 10 else onu_number

  return '{board_reference}{pon_id}{onu_reference}'.format(
    board_reference=board_reference,
    pon_id=pon_id,
    onu_reference=onu_reference
  )


class TestOutputMethods(unittest.TestCase):

  telnet_testing_environment = None

  @classmethod
  def setUpClass(cls):
    cls.telnet_testing_environment = TelnetTestingEnvironment(port=23236)
    cls.telnet_testing_environment.setup()

  @classmethod
  def tearDownClass(cls):
    cls.telnet_testing_environment.tear_down()

  def test_get_signal_power(self):
    for test in test_params.keys():
      data = get_signal_power(show_optic_module=test_data[test]['optic_module'])
      self.assertEqual(first=test_params[test]['signal_power'], second=data)

  @patch(target='tasiap.onu_signal_power.get_signal_power')
  @patch(target='tasiap.onu_signal_power.get_onu_number_from_id')
  @patch(target='tasiap.onu_signal_power.get_pon_id')
  @patch(target='tasiap.onu_signal_power.get_board_id')
  def test_get_onu_power_signal_by_id(
    self,
    mock_get_board_id,
    mock_get_pon_id,
    mock_get_onu_number_from_id,
    mock_get_signal_power
  ):
    telnet = MagicMock()
    onu_id = '1234'
    self.assertEqual(
      first=mock_get_signal_power.return_value,
      second=get_onu_power_signal_by_id(onu_id='1234', telnet=telnet),
      msg='Returns the signal power from get_onu_power_signal_by_id'
    )
    self.assertIn(
      member=[call(show_optic_module=telnet.read_until.return_value.decode.return_value)],
      container=mock_get_signal_power.mock_calls,
      msg=str(
        'Calls get_signal_power passing the show optic module data gathered from the telnet session passed '
        'decoded'
      )
    )
    self.assertEqual(
      first=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'Admin\\gpononu# '),
        call.write(
          'show optic_module slot {board_id} link {pon_id} onu {onu_number}\n'.format(
            board_id=mock_get_board_id.return_value,
            pon_id=mock_get_pon_id.return_value,
            onu_number=mock_get_onu_number_from_id.return_value
          ).encode('ascii')
        ),
        call.read_until(b'Admin\\gpononu# ', timeout=4),
        call.read_until().decode('ascii')
      ],
      second=telnet.mock_calls,
      msg=str(
        'Uses the telnet session passed to enter the gpononu directory and request the optic_module data using the '
        'parameters given by get_board_id, get_pon_id and get_onu_number_from_id as slot, link and onu (respectively). '
        'The response is read after each command written - after requesting the data from the optic_module though, the '
        'reading has a four seconds timeout and is decoded from ascii.'
      )
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_board_id.mock_calls,
      msg='Calls get_board_id with the onu_id passed'
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_pon_id.mock_calls,
      msg='Calls get_pon_id with the onu_id passed'
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_onu_number_from_id.mock_calls,
      msg='Calls get_onu_number_from_id with the onu_id passed'
    )
