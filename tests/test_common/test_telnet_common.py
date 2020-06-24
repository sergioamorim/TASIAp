from telnetlib import Telnet
from unittest import TestCase

from config import telnet_config
from tasiap.common.telnet_common import connect_su, str_to_telnet, supply_telnet_connection, get_wifi_data_effective, \
  get_ssid, get_wifi_password
from tests.data.telnet_testing_data import test_params, test_data
from tests.telnet_testing_environment import TelnetTestingEnvironment


class TestTelnetFunctions(TestCase):
  telnet_testing_environment = None

  @classmethod
  def setUpClass(cls):
    cls.telnet_testing_environment = TelnetTestingEnvironment(port=23623)
    cls.telnet_testing_environment.setup()

  @classmethod
  def tearDownClass(cls):
    cls.telnet_testing_environment.tear_down()

  def test_str_to_telnet(self):
    self.assertEqual(first=str_to_telnet(string='a'), second=b'a\n')
    self.assertEqual(first=str_to_telnet(string='a\n'), second=b'a\n\n')
    self.assertEqual(first=str_to_telnet(string='"a"'), second=b'"a"\n')

  def test_connect_su(self):
    with Telnet(host=telnet_config.ip, port=telnet_config.port) as tn:
      connect_su(tn=tn)
      tn.write(b'quit\n')
      tn.read_all()

  def test_supply_telnet_connection(self):

    @supply_telnet_connection
    def generic_function(tn=None):
      return repr(tn)

    with Telnet(host=telnet_config.ip, port=telnet_config.port) as tln:
      connect_su(tn=tln)
      self.assertEqual(first=generic_function(tn=tln), second=repr(tln))
      tln.write(b'quit\n')
      tln.read_all()

    self.assertNotEqual(first=generic_function(), second='None')

  def test_get_wifi_data_effective(self):
    for test in test_params.keys():
      data = get_wifi_data_effective(
        board_id=test_params[test]['board_id'],
        pon_id=test_params[test]['pon_id'],
        onu_number=test_params[test]['onu_number']
      )
      self.assertEqual(first=test_data[test]['wifi_serv'], second=data)

  def test_get_ssid(self):
    for test in test_params.keys():
      ssid = get_ssid(
        board_id=test_params[test]['board_id'],
        pon_id=test_params[test]['pon_id'],
        onu_number=test_params[test]['onu_number']
      )
      self.assertEqual(first=test_params[test]['ssid'], second=ssid)

  def test_get_wifi_password(self):
    for test in test_params.keys():
      wifi_password = get_wifi_password(
        board_id=test_params[test]['board_id'],
        pon_id=test_params[test]['pon_id'],
        onu_number=test_params[test]['onu_number']
      )
      self.assertEqual(first=test_params[test]['password'], second=wifi_password)
