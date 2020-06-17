from telnetlib import Telnet
from unittest import TestCase

from config import telnet_config
from tasiap.common.telnet_common import connect_su, str_to_telnet, supply_telnet_connection, get_wifi_data_effective, \
  get_ssid, get_wifi_password
from tests.data.telnet_testing_data import wifi_data_params, wifi_data
from tests.telnet_testing_environment import ServerThread


class TestTelnetFunctions(TestCase):
  server_thread = None

  @classmethod
  def setUpClass(cls):
    # the telnet_config.password_sudo is processed before runtime, at the AN551606BMockHandler class definition,
    # so the real password_sudo is used here. make sure to change telnet_config.username, telnet_config.password and
    # telnet_config.port to prevent mistakes; also, change the telnet_config.ip to localhost
    telnet_config.username = 'a'
    telnet_config.password = 'b'
    telnet_config.ip = 'localhost'  # hardcoded in the ServerThread constructor from telnet_testing_environment
    telnet_config.port = 23236
    cls.server_thread = ServerThread()
    cls.server_thread.start()

  @classmethod
  def tearDownClass(cls):
    cls.server_thread.stop()

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
    for test in wifi_data_params.keys():
      data = get_wifi_data_effective(
        board_id=wifi_data_params[test]['board_id'],
        pon_id=wifi_data_params[test]['pon_id'],
        onu_number=wifi_data_params[test]['onu_number']
      )
      self.assertEqual(first=data, second=wifi_data[test])

  def test_get_ssid(self):
    for test in wifi_data_params.keys():
      ssid = get_ssid(
        board_id=wifi_data_params[test]['board_id'],
        pon_id=wifi_data_params[test]['pon_id'],
        onu_number=wifi_data_params[test]['onu_number']
      )
      self.assertEqual(first=ssid, second=wifi_data_params[test]['ssid'])

  def test_get_wifi_password(self):
    for test in wifi_data_params.keys():
      wifi_password = get_wifi_password(
        board_id=wifi_data_params[test]['board_id'],
        pon_id=wifi_data_params[test]['pon_id'],
        onu_number=wifi_data_params[test]['onu_number']
      )
      self.assertEqual(first=wifi_password, second=wifi_data_params[test]['password'])
