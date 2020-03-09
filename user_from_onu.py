#!/usr/bin/env python3.8
# coding=utf-8

import argparse
from telnetlib import Telnet
import telnet_config
import mysqldb_config
from logger import logger
from mysql_common import get_mysql_session
from telnet_common import connect_su, get_next_value, str_to_telnet
from string_common import sanitize_cto_vlan_name, is_onu_id_valid
from sqlite_common import update_onu_info


def is_cto_id(session, onu_id):
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE AcctStopTime = '0000-00-00 00:00:00' AND " \
                     "CalledStationID LIKE '%{1}%' ORDER BY AcctStartTime DESC LIMIT 1;".format(
                      mysqldb_config.radius_acct_table, onu_id)
  if cto_vlan_name := session.execute(sql_query_string).scalar():
    return sanitize_cto_vlan_name(cto_vlan_name)
  if onu_id[:1] == '1':
    board = '12'
  else:
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:]
  cto_like_name = 'P{0}-PON{1}-ONU{2}'.format(board, pon, onu_number)
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE AcctStopTime = '0000-00-00 00:00:00' AND " \
                     "CalledStationID LIKE '%{1}%' ORDER BY AcctStartTime DESC LIMIT 1;".format(
                      mysqldb_config.radius_acct_table, cto_like_name)
  if cto_vlan_name := session.execute(sql_query_string).scalar():
    return sanitize_cto_vlan_name(cto_vlan_name)
  return None


def is_offline_cto_id(session, onu_id):
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%' ORDER BY " \
                     "AcctStopTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table, onu_id)
  if cto_vlan_name := session.execute(sql_query_string).scalar():
    return '{0} (offline)'.format(sanitize_cto_vlan_name(cto_vlan_name))
  if onu_id[:1] == '1':
    board = '12'
  else:
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:]
  cto_like_name = 'P{0}-PON{1}-ONU{2}'.format(board, pon, onu_number)
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%' ORDER BY " \
                     "AcctStopTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table, cto_like_name)
  if cto_vlan_name := session.execute(sql_query_string).scalar():
    return '{0} (offline)'.format(sanitize_cto_vlan_name(cto_vlan_name))
  return None


def get_mac_list_from_onu_id(onu_id):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
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
      logger.debug('get_mac_list_from_onu_id: while not found: waste value: {0}'.format(waste_value.replace('\r', '')))
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


def find_user_by_onu(onu_id):
  session = get_mysql_session()
  if cto := is_cto_id(session, onu_id):
    session.close()
    return cto
  if len((mac_list := get_mac_list_from_onu_id(onu_id))):
    username_list = []
    for mac in mac_list:
      sql_query_string = "SELECT DISTINCT UserName FROM {0} WHERE CallingStationID = :mac ORDER BY AcctStartTime ' \
      'DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
      if username := session.execute(sql_query_string, {'mac': mac}).scalar():
        username_list.append(username)
    if username_list:
      if len(username_list) == 1:
        update_onu_info(int(onu_id), username=username_list[0])
      session.close()
      return ' '.join(username_list)
  elif 'ERR' in mac_list:
    session.close()
    return 'ERR'
  elif cto := is_offline_cto_id(session, onu_id):
    session.close()
    return cto
  session.close()
  return None


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ONU id to find the username from the user connected to it',
                      default=None)
  args = parser.parse_args()

  if onu_id := args.i:
    if is_onu_id_valid(onu_id):
      print(find_user_by_onu(onu_id))
      return 0
    print('ID da ONU inválido.')
    return 1
  print('Informe o ID da ONU.')
  return 1


if __name__ == '__main__':
  main()
