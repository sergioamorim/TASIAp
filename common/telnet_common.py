from functools import wraps
from re import findall
from telnetlib import Telnet

from config import telnet_config
from logger import get_logger

logger = get_logger(__name__)


def supply_telnet_connection(function):
  @wraps(function)
  def telnet_connection_wrapper(*args, **kwargs):
    if 'tn' not in kwargs:
      with Telnet(telnet_config.ip, telnet_config.port) as tn:
        connect_su(tn)
        return function(*args, **kwargs, tn=tn)
    return function(*args, **kwargs)
  return telnet_connection_wrapper


def str_to_telnet(string):
  return string.encode('ascii') + b'\n'


def connect_su(tn):
  tn.read_until(b'Login: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.username))
  tn.read_until(b'Password: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.password))
  tn.read_until(b'User> ', timeout=1)
  tn.write(str_to_telnet('enable'))
  tn.read_until(b'Password: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.password_sudo))
  tn.read_until(b'Admin# ', timeout=1)
  tn.write(str_to_telnet('cd service'))
  tn.read_until(b'service# ', timeout=1)
  tn.write(str_to_telnet('terminal length 512'))
  tn.read_until(b'service# ', timeout=1)
  tn.write(str_to_telnet('cd ..'))
  tn.read_until(b'Admin# ', timeout=1)


@supply_telnet_connection
def get_wifi_data_effective(board_id, pon_id, onu_number, tn=None):
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ')
  tn.write(str_to_telnet('show wifi_serv slot {0} link {1} onu {2}'.format(board_id, pon_id, onu_number)))
  return tn.read_until(b'Admin\\gpononu# ').decode('ascii')


@supply_telnet_connection
def get_ssid(board_id, pon_id, onu_number, tn=None):
  ssid_pattern = '\\*\\*SSID:(.*?)\\n'
  wifi_data = get_wifi_data_effective(board_id, pon_id, onu_number, tn=tn)
  if ssid := findall(ssid_pattern, wifi_data):
    return ssid[0].replace('\r', '')
  logger.error('get_ssid: ssid not found')
  return None


@supply_telnet_connection
def get_wifi_password(board_id, pon_id, onu_number, tn=None):
  wifi_password_pattern = '\\*\\*WPA Share Key:(.*?)\\n'
  wifi_data = get_wifi_data_effective(board_id, pon_id, onu_number, tn=tn)
  if wifi_password := findall(wifi_password_pattern, wifi_data):
    return wifi_password[0].replace('\r', '')
  logger.error('get_wifi_password: password not found')
  return None
