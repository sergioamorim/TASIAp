import unittest

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

  def test_get_onu_power_signal_by_id(self):

      for test in test_params.keys():

        onu_id = translate_onu_id(
          board_id=test_params[test]['board_id'],
          pon_id=test_params[test]['pon_id'],
          onu_number=test_params[test]['onu_number']
        )

        data = get_onu_power_signal_by_id(onu_id=onu_id)

        self.assertEqual(first=test_params[test]['signal_power'], second=data)
