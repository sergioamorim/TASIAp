#!/usr/bin/python3.6
# coding=utf-8

import argparse
import logging
from telnetlib import Telnet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import telnet_config
import mysqldb_config

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

def sanitize_cto_name(cto_name):
  ## on development

def is_cto_id(session, onu_id):
  sql_query = session.execute("SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE :onu_id ORDER BY AcctStartTime DESC LIMIT 1;".format(
    mysqldb_config.radius_acct_table), {'onu_id': onu_id}).first()
  if sql_query:
    return sanitize_cto_name(login_query[0])
  if onu_id[:1] == '1':
    board = '12'
  else:
  # elif onu_id[:1] == '2':
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if onu_id[2:3] != '0' else onu_id[3:]
  sql_query = session.execute("SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE :cto_like_name ORDER BY AcctStartTime DESC LIMIT 1;".format(
    mysqldb_config.radius_acct_table), {'cto_like_name': 'P{0}-PON{1}-ONU{2}'.format(board, pon, onu_number)}).first()
  if sql_query:
    return sanitize_cto_name(login_query[0])
  return None

def get_username_by_onu_id(session, tn, onu_id):
  ## on development

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser consultada', default=None)
  args = parser.parse_args()

  onu_id = None
  if args.i:
    onu_id = str(args.i)

  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host, mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    username = get_username_by_onu_id(session, tn, onu_id)
    print(username)


if __name__ == '__main__':
  main()