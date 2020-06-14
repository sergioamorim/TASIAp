from telnetlib import Telnet
from unittest import TestCase

from config import telnet_config
from tasiap.common.telnet_common import connect_su, str_to_telnet, supply_telnet_connection


class TestTelnetFunctions(TestCase):

  @classmethod
  def setUpClass(cls):
    telnet_config.username = 'a'
    telnet_config.password = 'b'
    telnet_config.ip = '127.0.0.1'
    telnet_config.port = 23
    telnet_config.password_sudo = 'sudo_password'

  def test_str_to_telnet(self):
    self.assertEqual(first=str_to_telnet(string='a'), second=b'a\n')
    self.assertEqual(first=str_to_telnet(string='a\n'), second=b'a\n\n')
    self.assertEqual(first=str_to_telnet(string='"a"'), second=b'"a"\n')

  def test_connect_su(self):
    with Telnet(host=telnet_config.ip, port=telnet_config.port) as tn:
      connect_su(tn=tn)

  def test_supply_telnet_connection(self):

    @supply_telnet_connection
    def generic_function(tn=None):
      return repr(tn)

    with Telnet(host=telnet_config.ip, port=telnet_config.port) as tn:
      self.assertEqual(first=generic_function(tn=tn), second=repr(tn))

    self.assertNotEqual(first=generic_function(), second='None')
