#!/usr/bin/python3.6
# coding=utf-8

import argparse
import logging
from telnetlib import Telnet
import telnet_config

logger = logging.getLogger('user_from_onu')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('user_from_onu.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def str_to_telnet(string):
  return string.encode('ascii')+b'\n'

def connect_su(tn):
  tn.read_until(b'Login: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.user))
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

def get_username_by_onu_id(tn, onu_id):
  ## on development

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser consultada', default=None)
  args = parser.parse_args()

  onu_id = None
  if args.i:
    onu_id = str(args.i)
  
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    username = get_username_by_onu_id(tn, onu_id)
    print(username)


if __name__ == '__main__':
  main()