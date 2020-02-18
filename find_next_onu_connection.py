#!/usr/bin/env python3.8
# coding=utf-8

from mysql_common import get_mysql_session
from onu_id_from_username import get_onu_id_by_mac_and_pon, format_pon_name
from telnet_common import connect_su
from datetime import datetime, timedelta
from string_common import is_int
import telnet_config
import mysqldb_config

def one_day_has_passed(start_time, actual_time):
  time_format = '%Y-%m-%d %H:%M:%S'
  return datetime.strptime(actual_time, time_format) - datetime.strptime(start_time, time_format) > timedelta(days=1)

def insert_into_radius_login(session, rtype, username, attribute, op, value):
  query_string = "INSERT INTO {0} (type, user, attribute, op, value, enable) VALUES ('{1}', '{2}', '{3}', '{4}', "
  if is_int(value):
    query_string = query_string + '{5}'
  else:
    query_string = query_string + "'{5}'"
  query_string = query_string + ', 1);'
  session.execute(query_string.format(MYSQL['radius_login_table'], rtype, username, attribute, op, value))

def reauthorize_user(session, username, password):
  session.execute('DELETE FROM {0} WHERE user = :username;'.format(mysqldb_config.login_radius_table), {'username': username})
  login_info = session.execute('SELECT ip, pass FROM {0} WHERE user = :username'.format(mysqldb_config.login_table), {'username': username}).first()
  insert_into_radius_login(session, 'C', username, 'Simultaneous-Use', ':=', 1)
  insert_into_radius_login(session, 'C', username, 'User-Password', ':=', login_info['pass'])
  if login_info['ip'] != '':
    insert_into_radius_login(session, 'R', username, 'Framed-IP-Address', '==', reserved_ip)

def diagnose_connection(session, user):
  query_string = 'SELECT FramedIPAddress, AcctStopTime FROM {0} WHERE UserName = :username ORDER BY AcctStartTime DESC;'.format(mysqldb_config.radius_acct_table)
  if (connection_info := session.execute(query_string, {'username': user['user']}).first()):
    if connection_info['FramedIPAddress'][4:6] == '66':
      query_string = 'SELECT cliente_id, enable FROM {0} WHERE user = :username;'.format(mysql_config.login_table)
      if (login := session.execute(query_string, {'username': user['UserName']}).first()):
        if login['enable'] == 1:
          query_string = 'SELECT status FROM {0} WHERE id = :id;'.format(mysqldb_config.clientes_table)
          if (client_status := session.execute(query_string, {'id': login['cliente_id']}).scalar()) == 1:
            reauthorize_user(session, user['user'])
            diagnostic = 'erro, reinicie o roteador.'
          elif client_status == 2:
            diagnostic = 'bloqueada, pendência financeira.'
          elif client_status == 0:
            diagnostic = 'bloqueada, cadastro do cliente desativado.'
          else client_status:
            diagnostic = 'bloqueada, cadastro do cliente bloqueado manualmente.'
        else:
          diagnostic = 'bloqueada, o login está desativado.'
      else:
        return 'bloqueada, o usúario não existe.'
    else:
      if connection_info['AcctStopTime'] == '0000-00-00 00:00:00':
        return 'normal.\nIP: {0}'.format(connection_info['FramedIPAddress'])
      return 'conectou normalmente e em seguida desconectou.'
  return None

def find_onu_connection(onu_id):
  session = get_mysql_session()
  start_time = update_time = session.execute('SELECT NOW();').scalar()
  board_number = '12' if onu_id[0] == '1' else '14'
  checking_frequency = 4
  vlan_name = 'v{0}00-P{1}-PON{2}-CLIENTES-FIBRA'.format(onu_id[0:2], board_number, onu_id[1])
  tn_formated_pon_name = format_pon_name(vlan_name)
  while not found and not one_day_has_passed(start_time, update_time):
    update_time = session.execute('SELECT NOW();').scalar()
    query_string = 'SELECT user, pass, sucess, CallingStationId FROM {0} WHERE CalledStationId = :vlanname AND AcctStartTime > :updatetime ORDER BY AcctStartTime DESC;'.format(mysqldb_config.radius_postauth_table)
    users = session.execute(query_string, {'vlanname': vlan_name, 'updatetime': update_time}).all()
    if len(users):
      with Telnet(telnet_config.ip, telnet_config.port) as tn:
        connect_su(tn)
        for user in users:
          if (onu_id_from_user := get_onu_id_by_mac_and_pon(tn, user['CallingStationId'], tn_formated_pon_name)) == onu_id:
            diagnostic = diagnose_connection(session, user)
            if not diagnostic:
              times_tried = 1
              while not diagnostic or times_tried > 3:
                sleep(30)
                diagnostic = diagnose_connection(session, user)
                times_tried = times_tried + 1
              if not diagnostic:
                user = session.execute('SELECT user, pass, sucess, CallingStationId FROM {0} WHERE user = :username ORDER BY AcctStartTime DESC;'.format(mysqldb_config.radius_postauth_table), {'username': user['user']}).first()
                if updated_user_info['sucess'] == 0 and updated_user_info['pass'] == session.execute('SELECT pass FROM {0} WHERE user = :username;'.format(mysqldb_config.login_table), {'username': user['user']}):
                  reauthorize_user(session, user['user']):
                  diagnostic = 'erro, reinicie o roteador.'
                elif updated_user_info['sucess'] == 0:
                  diagnostic = 'erro, senha do usuário errada.'
                else:
                  diagnostic = 'desconhecido.'
            user_data = {'username': user['user'], 'password': user['pass'], 'diagnostic': diagnostic}
            return user_data
    sleep(checking_frequency)
    if checking_frequency < 120:
      checking_frequency = checking_frequency + checking_frequency
  return None