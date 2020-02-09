#!/usr/bin/python3.8
# coding=utf-8

import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telnetlib import Telnet
import mysqldb_config
import telnet_config
from telnet_common import connect_su, str_to_telnet, get_next_value

logger = logging.getLogger('onu_id_from_username')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/onu_id_from_username.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def get_onu_id_by_mac(mac):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    pon_list = get_pon_list(tn)
    tn.write(str_to_telnet('cd gponline'))
    tn.read_until(b'gponline# ', timeout=1)
    logger.debug('get_onu_id_by_mac: starting find mac: {0}'.format(mac))
    for pon in pon_list:
      tn.write(str_to_telnet('show pon_mac {0}'.format(pon)))
      remove_header_value = tn.read_until(b'-----\n\r001\t', timeout=1)
      logger.debug('get_onu_id_by_mac: remove_header: {0}'.format(remove_header_value))
      end_of_list = False
      if 'gponline#' in remove_header_value.decode('utf-8'):
        end_of_list = True
      while not end_of_list:
        value = get_next_value(tn, '\t')
        if '--Press' in value:
          logger.debug('get_onu_id_by_mac: while not found: catch --Press: value: {0}'.format(value))
          tn.write(str_to_telnet('\n'))
          tn.read_until(b'Master', timeout=1)
          value = get_next_value(tn, '\t')
        current_mac = value
        logger.debug('get_onu_id_by_mac: while not found: current_mac: {0}'.format(current_mac))
        get_next_value(tn, ' ')
        current_onu_number = get_next_value(tn, '\n')[6:]
        logger.debug('get_onu_id_by_mac: while not found: current_onu_number: {0}'.format(current_onu_number))
        if current_mac == mac:
          logger.debug('get_onu_id_by_mac: catch right mac: {0} == {1}'.format(current_mac, mac))
          onu_number = current_onu_number
          logger.debug('get_onu_id_by_mac: catch right mac: onu_number: {0}'.format(onu_number))
          pon_number = pon[13:15].replace(' ','')
          logger.debug('get_onu_id_by_mac: catch right mac: pon: {0}'.format(pon))
          board_id = '1' if pon[5:7] == '12' else '2'
          logger.debug('get_onu_id_by_mac: catch right mac: board: {0}'.format(board))
          return '{0}{1}{2}{3}'.format(board_id, pon_number, '0' if int(onu_number) < 10 else '', onu_number)
        waste_value = get_next_value(tn, '\t')
        logger.debug('get_onu_id_by_mac: while not found: waste_value: {0}'.format(waste_value.replace('\r','')))
        if 'gponline#' in waste_value:
          end_of_list = True
        elif 'stop--' in waste_value:
          logger.debug('get_onu_id_by_mac: while same_onu: catch --Press')
          tn.write(str_to_telnet('\n'))
          tn.read_until(b'Master', timeout=1)
          waste_value = get_next_value(tn, '\t')
  return None

def get_pon_list(tn):
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_auth all'))
  tn.read_until(b'ITEM=', timeout=1)
  pon_sum = get_next_value(tn, ' ')
  logger.debug('get_pon_list: pon_sum: {0}'.format(pon_sum))
  tn.read_until(b'\r', timeout=1)
  pon_list = []
  for i in range(0,int(pon_sum)):
    current_pon = tn.read_until(b' ,', timeout=1)[:-2].decode('utf-8')
    pon_list.append(current_pon)
    logger.debug('get_pon_list: pon_list finding loop: current_pon: {0}'.format(current_pon))
    waste_value = tn.read_until(b'\r', timeout=1).decode('utf-8')
    logger.debug('get_pon_list: pon_list finding loop: waste_value: {0}'.format(waste_value.replace('\r',' ')))
  logger.debug('get_pon_list: pon_list: {0}'.format(pon_list))
  waste_value = tn.read_until(b'gponline# ', timeout=1)
  logger.debug('get_pon_list: catch gponline#: {0}'.format(waste_value))
  tn.write(str_to_telnet('cd ..'))
  waste_value = tn.read_until(b'Admin# ', timeout=1)
  logger.debug('get_pon_list: catch Admin#: {0}'.format(waste_value))
  return pon_list

def find_onu_by_user(username):
  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host, mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  query_mac_string = "SELECT CallingStationID FROM {0} WHERE UserName = :username ORDER BY AcctStartTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
  if (mac := session.execute(query_mac_string, {'username': username}).scalar()):
    return get_onu_id_by_mac(mac)
  return None

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--username', dest='u', help='Usuario a ser consultado.', default=None)
  args = parser.parse_args()

  if (username := args.u):
    print(find_onu_by_user(username))
    return 0

  print('Informe o usuario.')
  return 1

if __name__ == '__main__':
  main()
