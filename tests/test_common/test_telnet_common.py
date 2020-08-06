from unittest import TestCase
from unittest.mock import call, MagicMock, patch

from config import telnet_config
from tasiap.common.telnet_common import sudo_authenticated, str_to_telnet, supply_telnet_session, \
  get_wifi_data_effective, \
  get_ssid, get_wifi_password, open_telnet_session, close_session


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
        call.read_until(b'Login: '),
        call.write('{username}\n'.format(username=telnet_config.username).encode('ascii')),
        call.read_until(b'Password: '),
        call.write('{password}\n'.format(password=telnet_config.password).encode('ascii')),
      ],
      'enable_sudo': [
        call.read_until(b'User> '),
        call.write(b'enable\n'),
        call.read_until(b'Password: '),
        call.write('{enable_password}\n'.format(enable_password=telnet_config.password_sudo).encode('ascii')),
        call.read_until(b'Admin# '),
      ],
      'terminal_length': [
        call.write(b'cd service\n'),
        call.read_until(b'service# '),
        call.write(b'terminal length 512\n'),
        call.read_until(b'service# '),
      ],
      'rest_in_root': [
        call.write(str_to_telnet('cd ..')),
        call.read_until(b'Admin# '),
      ],
    }

    sudo_authenticated(telnet=telnet)

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

  @patch(target='tasiap.common.telnet_common.open_telnet_session')
  def test_supply_telnet_connection(self, mock_telnet_connection_factory):
    @supply_telnet_session
    def generic_function(telnet=None):
      return telnet

    telnet_session = 'telnet session'
    self.assertEqual(
      first=generic_function(telnet=telnet_session),
      second=telnet_session,
      msg='When a telnet connection is passed to a function it is not overwritten'
    )
    self.assertEqual(
      first=mock_telnet_connection_factory().__enter__.return_value,
      second=generic_function(),
      msg='When no telnet connection is passed one is created from open_telnet_session and included in the call'
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
        telnet=telnet
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
        telnet=telnet
      ),
      msg='None is returned when no SSID is found in data from get_wifi_data_effective'
    )
    self.assertEqual(
      first=[call(board_id, pon_id, onu_number, telnet=telnet)],
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
        telnet=telnet
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
        telnet=telnet
      ),
      msg='None is returned when no wifi password is found in data from get_wifi_data_effective'
    )
    self.assertEqual(
      first=[call(board_id, pon_id, onu_number, telnet=telnet)],
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
        telnet=telnet
      ),
      msg='wifi password is returned when found in data from get_wifi_data_effective'
    )

  @patch(target='tasiap.common.telnet_common.close_session')
  @patch(target='tasiap.common.telnet_common.sudo_authenticated')
  @patch(target='tasiap.common.telnet_common.Telnet')
  def test_telnet_connection_factory(self, mock_telnet_class, mock_sudo_authenticated, mock_close_session):
    telnet_config.ip = 'ip'
    telnet_config.port = 'port'
    with open_telnet_session() as telnet:
      self.assertEqual(
        first=[call(host=telnet_config.ip, port=telnet_config.port)],
        second=mock_telnet_class.mock_calls,
        msg='Creates the connection using the ip and port from telnet_config'
      )
      self.assertEqual(
        first=[call(telnet=mock_telnet_class.return_value)],
        second=mock_sudo_authenticated.mock_calls,
        msg='Authenticates and enables sudo on the session created from the Telnet class'
      )
      self.assertEqual(
        first=mock_sudo_authenticated.return_value,
        second=telnet,
        msg='Returns the telnet session already authenticated and with sudo enabled'
      )
      self.assertEqual(
        first=[],
        second=mock_close_session.mock_calls,
        msg='Does not close the session while the context is open'
      )
    self.assertEqual(
      first=[call(telnet=mock_telnet_class.return_value)],
      second=mock_close_session.mock_calls,
      msg='Closes the session after the context is closed'
    )

  def test_close_session(self):
    telnet = MagicMock()
    close_session(telnet=telnet)
    self.assertEqual(
      first=[
        call.write(b'cd ..\n'),
        call.write(b'quit\n'),
        call.read_until(b'ye!\r\n', timeout=1),
        call.close()
      ],
      second=telnet.mock_calls,
      msg=str(
        r'Uses the telnet session passed to return to the root directory, use the quit command and read all the output '
        r'available after the quit command (expecting for the last characters to be "ye!\r\n") and then effectively '
        r'closes the session.'
      )
    )
