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
def get_wifi_data_effective(onu_address, telnet=None):
  telnet.write(b'cd gpononu\n')
  telnet.read_until(b'Admin\\gpononu# ')
  telnet.write(
    'show wifi_serv slot {board_id} link {pon_id} onu {onu_number}\n'.format(
      board_id=onu_address['board_id'],
      pon_id=onu_address['pon_id'],
      onu_number=onu_address['onu_number']
    ).encode('ascii')
  )
  return telnet.read_until(b'Admin\\gpononu# ').decode('ascii')


def ssid(wifi_serv):
  if (current_ssid := findall(
    pattern='\\*\\*SSID:(.*?)\\n',
    string=wifi_serv
  )) and current_ssid != ['\r']:
    return current_ssid[0].replace('\r', '')

  logger.error('ssid not found in {wifi_serv!r}'.format(wifi_serv=wifi_serv))
  return None


@supply_telnet_session
def get_ssid(onu_address, telnet=None):
  return ssid(wifi_serv=get_wifi_data_effective(
    onu_address=onu_address,
    telnet=telnet
  ))


def wpa_key(wifi_serv):
  if (current_wpa_key := findall(
    pattern='\\*\\*WPA Share Key:(.*?)\\n',
    string=wifi_serv
  )) and current_wpa_key != ['\r']:
    return current_wpa_key[0].replace('\r', '')

  logger.error('wpa_key not found in {wifi_serv!r}'.format(wifi_serv=wifi_serv))
  return None


@supply_telnet_session
def get_wifi_password(onu_address, telnet=None):
  return wpa_key(wifi_serv=get_wifi_data_effective(
    onu_address=onu_address,
    telnet=telnet
  ))
