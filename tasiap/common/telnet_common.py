from contextlib import contextmanager
from functools import wraps
from re import findall
from telnetlib import Telnet

from config import telnet_config
from tasiap.logger import get_logger

logger = get_logger(__name__)


def supply_telnet_session(function):
  @wraps(function)
  def telnet_connection_wrapper(*args, **kwargs):
    if 'telnet' not in kwargs:
      with open_telnet_session() as telnet:
        return function(*args, **kwargs, telnet=telnet)
    return function(*args, **kwargs)

  return telnet_connection_wrapper


@contextmanager
def open_telnet_session():
  telnet = Telnet(host=telnet_config.ip, port=telnet_config.port)
  try:
    yield sudo_authenticated(telnet=telnet)
  finally:
    close_session(telnet=telnet)


def close_session(telnet):
  telnet.write(b'cd ..\n')
  telnet.write(b'quit\n')
  telnet.read_until(b'ye!\r\n', timeout=1)
  telnet.close()


def str_to_telnet(string):
  return string.encode('ascii') + b'\n'


def sudo_authenticated(telnet):
  telnet.read_until(b'Login: ')
  telnet.write('{username}\n'.format(
    username=telnet_config.username
  ).encode('ascii'))

  telnet.read_until(b'Password: ')
  telnet.write('{password}\n'.format(
    password=telnet_config.password
  ).encode('ascii'))

  telnet.read_until(b'User> ')
  telnet.write(b'enable\n')
  telnet.read_until(b'Password: ')
  telnet.write('{enable_password}\n'.format(
    enable_password=telnet_config.password_sudo
  ).encode('ascii'))

  telnet.read_until(b'Admin# ')
  telnet.write(b'cd service\n')

  telnet.read_until(b'service# ')
  telnet.write(b'terminal length 512\n')

  telnet.read_until(b'service# ')
  telnet.write(b'cd ..\n')

  telnet.read_until(b'Admin# ')
  return telnet


@supply_telnet_session
def get_wifi_data_effective(board_id, pon_id, onu_number, telnet=None):
  telnet.write(str_to_telnet('cd gpononu'))
  telnet.read_until(b'Admin\\gpononu# ')
  telnet.write(str_to_telnet('show wifi_serv slot {0} link {1} onu {2}'.format(board_id, pon_id, onu_number)))
  return telnet.read_until(b'Admin\\gpononu# ').decode('ascii')


@supply_telnet_session
def get_ssid(board_id, pon_id, onu_number, telnet=None):
  ssid_pattern = '\\*\\*SSID:(.*?)\\n'
  wifi_data = get_wifi_data_effective(board_id, pon_id, onu_number, telnet=telnet)
  if ssid := findall(ssid_pattern, wifi_data):
    return ssid[0].replace('\r', '')
  logger.error('get_ssid: ssid not found')
  return None


@supply_telnet_session
def get_wifi_password(board_id, pon_id, onu_number, telnet=None):
  wifi_password_pattern = '\\*\\*WPA Share Key:(.*?)\\n'
  wifi_data = get_wifi_data_effective(board_id, pon_id, onu_number, telnet=telnet)
  if wifi_password := findall(wifi_password_pattern, wifi_data):
    return wifi_password[0].replace('\r', '')
  logger.error('get_wifi_password: password not found')
  return None
