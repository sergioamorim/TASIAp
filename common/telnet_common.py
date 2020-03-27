from functools import wraps
from telnetlib import Telnet

from config import telnet_config


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
