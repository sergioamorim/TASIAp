#!/usr/bin/python3.6
# coding=utf-8

import argparse
import logging
from telnetlib import Telnet
import telnet_config

logger = logging.getLogger('onu_signal_power')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('onu_signal_power.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def str_to_telnet(string):
  return string.encode('ascii')+b'\n'

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

def is_int(s):
  try: 
    int(s)
    return True
  except ValueError:
    return False

def get_next_value(tn, char):
  value = tn.read_until(char.encode('ascii'), timeout=1)
  logger.debug('get_next_value: first catch: {0}'.format(value[:-1]))
  while char.encode('ascii') in value[:-1] or char.encode('ascii') is value:
    value = tn.read_until(char.encode('ascii'), timeout=1)
    logger.debug('get_next_value: next catch: {0}'.format(value[:-1]))
  logger.debug('get_next_value: return: {0}'.format(value[:-1]))
  return value[:-1].decode('utf-8')

def get_onu_power_signal_by_id(tn, onu_id):
  if is_int(onu_id) and int(onu_id) > 0 and int(onu_id) < 4096:
    if onu_id[:1] == '1':
      board = '12'
    elif onu_id[:1] == '2':
      board = '14'
    else:
      raise ValueError('The first digit of the given ID is invalid (only 1 and 2 are accepted).')
    pon = onu_id[1:2]
    if int(pon) < 1 or int(pon) > 8:
      raise ValueError('The second digit of the given ID is out of range (1 to 8 are accepted)')
    onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
    if int(onu_number) < 1:
      raise ValueError('The last two digits of the given ID are invalid (needs to be greater than 00)')
    tn.write(str_to_telnet('cd gpononu'))
    waste_value = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8').replace('\r','')
    logger.debug('get_onu_power_signal_by_id: waste_value 1: {0}'.format(waste_value))
    if 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      waste_value = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8').replace('\r','')
      logger.debug('get_onu_power_signal_by_id: waste_value 2: {0}'.format(waste_value))
    tn.write(str_to_telnet('show optic_module slot {0} link {1} onu {2}'.format(board, pon, onu_number)))
    logger.debug('get_onu_power_signal_by_id: tn.write: {0}'.format(repr('show optic_module slot {0} link {1} onu {2}'.format(board, pon, onu_number))))
    waste_value = tn.read_until(b'\n', timeout=3).decode('utf-8').replace('\r','')
    logger.debug('get_onu_power_signal_by_id: waste_value 3: {0}'.format(waste_value))
    if 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      waste_value = tn.read_until(b'\n', timeout=3).decode('utf-8').replace('\r','')
      logger.debug('get_onu_power_signal_by_id: waste_value 4: {0}'.format(waste_value))
    value = get_next_value(tn, ' ')
    logger.debug('get_onu_power_signal_by_id: try to catch -553: {0}'.format(value))
    if value != '-----':
      value = get_next_value(tn, ']')
      if '-553' in value:
        signal_power = 'off'
      elif '-506' in value:
        signal_power = 'not found'
      else:
        signal_power = 'error'
    else:
      waste_value = tn.read_until(b'RECV POWER   :', timeout=3).decode('utf-8').replace('\r','')
      logger.debug('get_onu_power_signal_by_id: waste_value 5: {0}'.format(waste_value))
      if 'stop--' in waste_value:
        tn.write(str_to_telnet('\n'))
        waste_value = tn.read_until(b'RECV POWER   :', timeout=3).decode('utf-8').replace('\r','')
        logger.debug('get_onu_power_signal_by_id: waste_value 6: {0}'.format(waste_value))
      signal_power = get_next_value(tn, '\t')[1:]
    logger.debug('get_onu_power_signal_by_id: signal_power: {0}'.format(signal_power))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('cd ..'))
    tn.read_until(b'Admin# ', timeout=1)
    return signal_power
  raise ValueError('The given ONU id is out of range (1 to 4095)')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser consultada', default=None)
  args = parser.parse_args()

  onu_id = None
  if args.i:
    onu_id = str(args.i)
  
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    signal_power = get_onu_power_signal_by_id(tn, onu_id)
    print(signal_power)

if __name__ == '__main__':
  main()