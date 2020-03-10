#!/usr/bin/python3.6
# coding=utf-8

import argparse
from telnetlib import Telnet

from common.string_common import is_int
from config import telnet_config
from logger import logger


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


def get_next_value(tn, char):
  value = tn.read_until(char.encode('ascii'), timeout=1)
  logger.debug('get_next_value: first catch: {0}'.format(value[:-1]))
  while char.encode('ascii') in value[:-1] or char.encode('ascii') is value:
    value = tn.read_until(char.encode('ascii'), timeout=1)
    logger.debug('get_next_value: next catch: {0}'.format(value[:-1]))
  logger.debug('get_next_value: return: {0}'.format(value[:-1]))
  return value[:-1].decode('utf-8')


def restart_onu_by_id(tn, onu_id):
  if is_int(onu_id) and 0 < int(onu_id) < 4096:
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
    waste_value = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8').replace('\r', '')
    logger.debug('restart_onu_by_id: waste_value 1: {0}'.format(waste_value))
    if 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      waste_value = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8').replace('\r', '')
      logger.debug('restart_onu_by_id: waste_value 2: {0}'.format(waste_value))
    tn.write(str_to_telnet('reset slot {0} link {1} onulist {2}'.format(board, pon, onu_number)))
    logger.debug('restart_onu_by_id: tn.write: {0}'.format(
      repr('reset slot {0} link {1} onulist {2}'.format(board, pon, onu_number))))
    waste_value = tn.read_until(b'\n', timeout=3).decode('utf-8').replace('\r', '')
    logger.debug('restart_onu_by_id: waste_value 3: {0}'.format(waste_value))
    if 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      waste_value = tn.read_until(b'\n', timeout=3).decode('utf-8').replace('\r', '')
      logger.debug('restart_onu_by_id: waste_value 4: {0}'.format(waste_value))
    value = get_next_value(tn, '!')
    logger.debug('restart_onu_by_id: reset command result: {0}'.format(value))
    if 'no onu satisfy the list' in value:
      restart_result = 'not found'
    elif 'reset onu ok' in value:
      restart_result = 'done'
    else:
      restart_result = 'error'
    logger.debug('restart_onu_by_id: reset command result: {0}'.format(restart_result))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('cd ..'))
    tn.read_until(b'Admin# ', timeout=1)
    return restart_result
  raise ValueError('The given ONU id is out of range (1 to 4095)')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser reiniciada', default=None)
  args = parser.parse_args()

  onu_id = None
  if args.i:
    onu_id = str(args.i)

  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    restart_result = restart_onu_by_id(tn, onu_id)
    print(restart_result)


if __name__ == '__main__':
  main()
