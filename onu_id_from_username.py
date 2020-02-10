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

def get_onu_id_by_mac_and_pon(tn, mac, pon):
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_mac {0} lookup {1}'.format(pon, mac.replace(':', ''))))
  tn.read_until(b'-----\n\r', timeout=1)
  value = get_next_value(tn, '\t')
  if 'gponline#' in value:
    return None
  tn.read_until(b'OnuId:', timeout=1)
  onu_number = get_next_value(tn, '\n')
  board_id = '1' if pon[5:7] == '12' else '2'
  return '{0}{1}{2}{3}'.format(board_id, pon[13:], '0' if int(onu_number) < 10 else '', onu_number)

def get_onu_id_by_mac(mac, pon):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    if pon:
      if (onu_id := get_onu_id_by_mac_and_pon(tn, mac, pon)):
        return onu_id
    pon_list = get_pon_list(tn)
    if pon:
      pon_list.remove(pon)
    for pon in pon_list:
      if (onu_id := get_onu_id_by_mac_and_pon(tn, mac, pon)):
        return onu_id
  return None

def get_pon_list(tn):
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_auth all'))
  tn.read_until(b'ITEM=', timeout=1)
  pon_sum = get_next_value(tn, ' ')
  tn.read_until(b'\r', timeout=1)
  pon_list = []
  for i in range(0,int(pon_sum)):
    current_pon = tn.read_until(b' ,', timeout=1)[:-2].decode('utf-8')
    pon_list.append(current_pon)
    tn.read_until(b'\r', timeout=1).decode('utf-8')
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('cd ..'))
  tn.read_until(b'Admin# ', timeout=1)
  return pon_list

def format_pon_name(vlan_name):
  if len(vlan_name) > 13 and vlan_name[5:7] == '-P' and vlan_name[9:13] == '-PON':
    return 'slot {0} link {1}'.format(vlan_name[7:9], vlan_name[13:14])
  return None

def find_onu_by_user(username):
  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host, mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  query_string = "SELECT CallingStationId, CalledStationId FROM {0} WHERE UserName = :username ORDER BY AcctStartTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
  if (query_result := session.execute(query_string, {'username': username}).first()):
    mac = query_result['CallingStationId']
    vlan_name = query_result['CalledStationId']
    pon = format_pon_name(vlan_name)
    if (onu_id := get_onu_id_by_mac(mac, pon)):
      return onu_id
    if pon:
      return 'offline - vlan: {0}'.format(vlan_name[1:5])
    return 'no pon - vlan: {0}'.format(vlan_name[1:5])
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