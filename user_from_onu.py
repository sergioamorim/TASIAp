#!/usr/bin/env python3.8
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
file_handler = logging.FileHandler('logs/user_from_onu.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

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

def get_next_value(tn, char):
  value = tn.read_until(char.encode('ascii'), timeout=1)
  logger.debug('get_next_value: first catch: {0}'.format(value[:-1]))
  while char.encode('ascii') in value[:-1] or char.encode('ascii') is value:
    value = tn.read_until(char.encode('ascii'), timeout=1)
    logger.debug('get_next_value: next catch: {0}'.format(value[:-1]))
  logger.debug('get_next_value: return: {0}'.format(value[:-1]))
  return value[:-1].decode('utf-8')

def sanitize_cto_vlan_name(cto_vlan_name):
  vlan = cto_vlan_name[:5]
  if cto_vlan_name[7:9] == '12':
    board_id = '1'
  else:
    board_id = '2'
  pon = cto_vlan_name[13:14]
  onu_number = cto_vlan_name[18:20]
  onu_id = '{0}{1}{2}'.format(board_id, pon, onu_number)
  cto_actual_name = cto_vlan_name[31:].replace('-',' ')
  cto_sanitized_name = 'CTO {0}{1}{2}'.format(onu_id, ' ({0}) '.format(vlan) if vlan[1:] != onu_id else ' ', cto_actual_name)
  return cto_sanitized_name

def is_cto_id(session, onu_id):
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE AcctStopTime = '0000-00-00 00:00:00' AND CalledStationID LIKE '%{1}%' ORDER BY AcctStartTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table, onu_id)
  if (cto_vlan_name := session.execute(sql_query_string).scalar()):
    return sanitize_cto_vlan_name(cto_vlan_name)
  if onu_id[:1] == '1':
    board = '12'
  else:
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:]
  cto_like_name = 'P{0}-PON{1}-ONU{2}'.format(board, pon, onu_number)
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE AcctStopTime = '0000-00-00 00:00:00' AND CalledStationID LIKE '%{1}%' ORDER BY AcctStartTime DESC LIMIT 1;".format(
    mysqldb_config.radius_acct_table, cto_like_name)
  if (cto_vlan_name := session.execute(sql_query_string).scalar()):
    return sanitize_cto_vlan_name(cto_vlan_name)
  return None

def is_onu_id_valid(onu_id):
  return is_int(onu_id) and int(onu_id) > 1100 and int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9

def get_mac_list_from_onu_id(tn, onu_id):
  if onu_id[:1] == '1':
    board = '12'
  else:
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
  associated_mac_list = []
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_mac slot {0} link {1}'.format(board, pon)))
  remove_header_value = tn.read_until(b'-----\n\r001\t', timeout=1)
  logger.debug('get_mac_list_from_onu_id: remove_header: {0}'.format(remove_header_value))
  if 'gponline#' in remove_header_value.decode('utf-8'):
    logger.error('get_mac_list_from_onu_id: onu not found!')
    return ['ERR']
  found = False
  logger.debug('get_mac_list_from_onu_id: starting find onu_number: {0}'.format(onu_number))
  while not found:
    value = get_next_value(tn, '\t')
    if '--Press' in value:
      logger.debug('get_mac_list_from_onu_id: while not found: catch --Press: value: {0}'.format(value))
      tn.write(str_to_telnet('\n'))
      tn.read_until(b'Master', timeout=1)
      value = get_next_value(tn, '\t')
    current_mac = value
    logger.debug('get_mac_list_from_onu_id: while not found: current_mac: {0}'.format(current_mac))
    current_vlan = get_next_value(tn, ' ')[4:]
    logger.debug('get_mac_list_from_onu_id: while not found: current_vlan: {0}'.format(current_vlan))
    current_onu_number = get_next_value(tn, '\n')[6:]
    logger.debug('get_mac_list_from_onu_id: while not found: current_onu_number: {0}'.format(current_onu_number))
    waste_value = get_next_value(tn, '\t')
    logger.debug('get_mac_list_from_onu_id: while not found: waste value: {0}'.format(waste_value.replace('\r','')))
    if 'gponline#' in waste_value:
      logger.error('get_mac_list_from_onu_id: onu not found!')
      return ['ERR']
    if current_onu_number == onu_number:
      logger.debug('get_mac_list_from_onu_id: catch right onu_number')
      associated_mac_list.append(current_mac)
      vlan = current_vlan
      found = True
  same_onu = True
  while same_onu:
    value = get_next_value(tn, '\t')
    if value == '--Press':
      logger.debug('get_mac_list_from_onu_id: while same_onu: catch --Press')
      tn.write(str_to_telnet('\n'))
      tn.read_until(b'Master', timeout=1)
      value = get_next_value(tn, '\t')
    current_mac = value
    logger.debug('get_mac_list_from_onu_id: while same_onu: current_mac: {0}'.format(current_mac))
    current_vlan = get_next_value(tn, ' ')[4:]
    logger.debug('get_mac_list_from_onu_id: while same_onu: current_vlan: {0}'.format(current_vlan))
    if current_vlan == vlan:
      logger.debug('get_mac_list_from_onu_id: while same_onu: same vlan')
      current_onu_number = get_next_value(tn, '\n')[6:]
      logger.debug('get_mac_list_from_onu_id: while same_onu: current_onu_number: {0}'.format(current_onu_number))
      if current_onu_number == onu_number:
        logger.debug('get_mac_list_from_onu_id: while same_onu: same vlan: same onu_number')
        associated_mac_list.append(current_mac)
        waste_value = get_next_value(tn, '\t')
        logger.debug('get_mac_list_from_onu_id: while not found: waste value: {0}'.format(waste_value))
      else:
        logger.debug('get_mac_list_from_onu_id: while same_onu: same vlan: different onu_number'.format)
        same_onu = False
    else:
      logger.debug('get_mac_list_from_onu_id: while same_onu: different vlan')
      same_onu = False
  waste_value = tn.read_until(b'gponline# ', timeout=1).decode('utf-8')
  logger.debug('get_mac_list_from_onu_id: finalizing: catch gponline#: waste_value: {0}'.format(waste_value))
  while 'stop--' in waste_value:
    tn.write(str_to_telnet('\n'))
    logger.debug('get_mac_list_from_onu_id: finalizing: catch stop--: waste_value: {0}'.format(waste_value))
    waste_value = tn.read_until(b'gponline# ', timeout=1).decode('utf-8')
    logger.debug('get_mac_list_from_onu_id: finalizing: catch gponline#: waste_value: {0}'.format(waste_value))
  tn.write(str_to_telnet('cd ..'))
  tn.read_until(b'Admin# ', timeout=1)
  logger.debug('get_mac_list_from_onu_id: stoped...')
  return associated_mac_list

def get_username_by_onu_id(session, tn, onu_id):
  if len((mac_list := get_mac_list_from_onu_id(tn, onu_id))):
    username_list = []
    for mac in mac_list:
      sql_query_string = "SELECT DISTINCT UserName FROM {0} WHERE CallingStationID = :mac ORDER BY AcctStartTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
      if (username := session.execute(sql_query_string, {'mac': mac}).scalar()):
        username_list.append(username)
    if username_list:
      return ' '.join(username_list)
  elif 'ERR' in mac_list:
    return 'ERR'
  return None

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ONU id to find the username from the user connected to it', default=None)
  args = parser.parse_args()

  onu_id = None
  if args.i:
    onu_id = str(args.i)
    if not is_onu_id_valid(onu_id):
      raise ValueError('The given onu id is invalid. The first digit of the id must be between 1 to 3 (board id), the second digit must be between 1 to 8 (pon number) and the last 2 digits must be between 01 and 99 (onu number).')

  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host, mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()

  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    if (cto := is_cto_id(session, onu_id)):
      print(cto)
    else:
      username = get_username_by_onu_id(session, tn, onu_id)
      print(username)

if __name__ == '__main__':
  main()