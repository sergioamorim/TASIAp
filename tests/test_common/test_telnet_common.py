from telnetlib import Telnet
from unittest import TestCase
from unittest.mock import call, MagicMock, patch

from config import telnet_config
from tasiap.common.telnet_common import connect_su, str_to_telnet, supply_telnet_connection, get_wifi_data_effective, \
  get_ssid, get_wifi_password, telnet_connection_factory
from tests.telnet_testing_environment import TelnetTestingEnvironment


class TestTelnetFunctions(TestCase):

  def test_str_to_telnet(self):
    self.assertEqual(first=str_to_telnet(string='a'), second=b'a\n')
    self.assertEqual(first=str_to_telnet(string='a\n'), second=b'a\n\n')
    self.assertEqual(first=str_to_telnet(string='"a"'), second=b'"a"\n')

  def test_connect_su(self):
    telnet_config.username = 'username from config'
    telnet_config.password = 'password from config'
    telnet = MagicMock()

    expected_calls = {
      'login': [
        call.read_until(b'Login: ', timeout=1),
        call.write('{username}\n'.format(username=telnet_config.username).encode('ascii')),
        call.read_until(b'Password: ', timeout=1),
        call.write('{password}\n'.format(password=telnet_config.password).encode('ascii')),
      ],
      'enable_sudo': [
        call.read_until(b'User> ', timeout=1),
        call.write(b'enable\n'),
        call.read_until(b'Password: ', timeout=1),
        call.write('{enable_password}\n'.format(enable_password=telnet_config.password_sudo).encode('ascii')),
        call.read_until(b'Admin# ', timeout=1),
      ],
      'terminal_length': [
        call.write(b'cd service\n'),
        call.read_until(b'service# ', timeout=1),
        call.write(b'terminal length 512\n'),
        call.read_until(b'service# ', timeout=1),
      ],
      'rest_in_root': [
        call.write(str_to_telnet('cd ..')),
        call.read_until(b'Admin# ', timeout=1),
      ],
    }

    connect_su(tn=telnet)

    self.assertEqual(
      first=expected_calls['login'],
      second=telnet.mock_calls[:4],
      msg='The first telnet calls are logging in with credentials from config'
    )

    self.assertEqual(
      first=expected_calls['enable_sudo'],
      second=telnet.mock_calls[4:9],
      msg='After the login is made, the next 5 telnet calls are enabling sudo with password from config'
    )

    self.assertEqual(
      first=expected_calls['terminal_length'],
      second=telnet.mock_calls[9:13],
      msg='After sudo is enabled, the next 4 telnet calls are setting the terminal length to 512'
    )

    self.assertEqual(
      first=expected_calls['rest_in_root'],
      second=telnet.mock_calls[-2:],
      msg='The last two telnet calls are putting the session to rest in the root of sudo (Admin#)'
    )

  @patch(target='tasiap.common.telnet_common.telnet_connection_factory')
  def test_supply_telnet_connection(self, mock_telnet_connection_factory):

    @supply_telnet_connection
    def generic_function(tn=None):
      return tn

    telnet = 'telnet connection'
    self.assertEqual(
      first=generic_function(tn=telnet),
      second=telnet,
      msg='When a telnet connection is passed to a function it is not overwritten'
    )
    self.assertEqual(
      first=mock_telnet_connection_factory().__enter__.return_value,
      second=generic_function(),
      msg='When no telnet connection is passed one is created from telnet_connection_factory and included in the call'
    )

  def test_get_wifi_data_effective(self):
    board_id = '12'
    pon_id = '1'
    onu_number = '1'

    telnet = MagicMock()
    telnet.read_until.return_value = b'binary data'
    expected_calls = [
      call.write(b'cd gpononu\n'),
      call.read_until(b'Admin\\gpononu# '),
      call.write('show wifi_serv slot {board_id} link {pon_id} onu {onu_number}\n'.format(
        board_id=board_id, pon_id=pon_id, onu_number=onu_number
      ).encode('ascii')),
      call.read_until(b'Admin\\gpononu# '),
    ]
    self.assertEqual(
      first=telnet.read_until.return_value.decode('ascii'),
      second=get_wifi_data_effective(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        tn=telnet
      ),
      msg='The data captured with read_until is decoded from ascii and returned'
    )

    self.assertEqual(
      first=expected_calls,
      second=telnet.mock_calls,
      msg='Entered gpononu directory, called show wifi_serv with the parameters passed and read everything in between'
    )

  @patch(target='tasiap.common.telnet_common.get_wifi_data_effective')
  def test_get_ssid(self, mock_get_wifi_data_effective):
    board_id = '12'
    pon_id = '1'
    onu_number = '1'
    ssid = 'network ssid'
    telnet = 'telnet connection'

    mock_get_wifi_data_effective.return_value = 'data without ssid'
    self.assertIsNone(
      obj=get_ssid(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        tn=telnet
      ),
      msg='None is returned when no SSID is found in data from get_wifi_data_effective'
    )
    self.assertEqual(
      first=[call(board_id, pon_id, onu_number, tn=telnet)],
      second=mock_get_wifi_data_effective.mock_calls,
      msg=str(
        'get_wifi_data_effective is called with the parameters passed to identify the onu and the already open telnet '
        'connection'
      )
    )

    mock_get_wifi_data_effective.return_value = str(
      '...'
      'SSID Index:1\r\n'
      '**SSID:{ssid}\r\n'
      '**SSID Enable/Disable:enable\r\n'
      '...'
    ).format(ssid=ssid)
    self.assertEqual(
      first=ssid,
      second=get_ssid(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        tn=telnet
      ),
      msg='SSID is returned when found in data from get_wifi_data_effective'
    )

  @patch(target='tasiap.common.telnet_common.get_wifi_data_effective')
  def test_get_wifi_password(self, mock_get_wifi_data_effective):
    board_id = '12'
    pon_id = '1'
    onu_number = '1'
    wifi_password = 'network ssid'
    telnet = 'telnet connection'

    mock_get_wifi_data_effective.return_value = 'data without wifi password'
    self.assertIsNone(
      obj=get_wifi_password(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        tn=telnet
      ),
      msg='None is returned when no wifi password is found in data from get_wifi_data_effective'
    )
    self.assertEqual(
      first=[call(board_id, pon_id, onu_number, tn=telnet)],
      second=mock_get_wifi_data_effective.mock_calls,
      msg=str(
        'get_wifi_data_effective is called with the parameters passed to identify the onu and the already open telnet '
        'connection'
      )
    )

    mock_get_wifi_data_effective.return_value = str(
      '...'
      '**Wlan Encrypt Type:aes\r\n'
      '**WPA Share Key:{password}\r\n'
      '**WPA Key Interval:0\r\n'
      '...'
    ).format(password=wifi_password)
    self.assertEqual(
      first=wifi_password,
      second=get_wifi_password(
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
        tn=telnet
      ),
      msg='wifi password is returned when found in data from get_wifi_data_effective'
    )

  def test_telnet_connection_factory(self):
    telnet_testing_environment = TelnetTestingEnvironment(port=23623)
    telnet_testing_environment.setup()

    with telnet_connection_factory() as tn:
      self.assertTrue(expr=tn)
      self.assertEqual(first=Telnet, second=type(tn))
      self.assertTrue(expr=tn.sock)
      self.assertFalse(expr=tn.eof)
      tn.write(b'cd ..\n')
      self.assertEqual(first=b'\r\nAdmin# ', second=tn.read_until(b'Admin# ', timeout=1))

    self.assertFalse(expr=tn.sock)
    self.assertTrue(expr=tn.eof)

    telnet_testing_environment.tear_down()
