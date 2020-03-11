from datetime import timedelta
from telnetlib import Telnet
from time import sleep

from common.mysql_common import get_mysql_session, reauthorize_user
from common.telnet_common import connect_su
from config import mysqldb_config, telnet_config
from logger import get_logger
from onu_id_from_username import get_onu_id_by_mac_and_pon, format_pon_name

logger = get_logger(__name__)


def one_day_has_passed(start_time, actual_time):
  return actual_time - start_time > timedelta(days=1)


def diagnose_connection(session, user):
  query_string = 'SELECT FramedIPAddress, AcctStopTime FROM {0} WHERE UserName = :username ORDER BY AcctStartTime ' \
                 'DESC;'.format(mysqldb_config.radius_acct_table)
  if connection_info := session.execute(query_string, {'username': user['user']}).first():
    logger.debug('diagnose_connection: connection_info: {0}'.format(connection_info))
    if connection_info['FramedIPAddress'][4:6] == '66':
      query_string = 'SELECT cliente_id, enable FROM {0} WHERE user = :username;'.format(mysqldb_config.login_table)
      if login := session.execute(query_string, {'username': user['UserName']}).first():
        if login['enable'] == 1:
          query_string = 'SELECT status FROM {0} WHERE id = :id;'.format(mysqldb_config.clientes_table)
          if (client_status := session.execute(query_string, {'id': login['cliente_id']}).scalar()) == 1:
            reauthorize_user(session, user['user'])
            return 'erro, reinicie o roteador.'
          elif client_status == 2:
            return 'bloqueada, pendência financeira.'
          elif client_status == 0:
            return 'bloqueada, cadastro do cliente desativado.'
          else:
            return 'bloqueada, cadastro do cliente bloqueado manualmente.'
        else:
          return 'bloqueada, o login está desativado.'
      else:
        return 'bloqueada, o usúario não existe.'
    else:
      if not connection_info['AcctStopTime']:
        return 'normal.\nIP: {0}'.format(connection_info['FramedIPAddress'])
      return 'conectou normalmente e em seguida desconectou.'
  return None


def find_onu_connection(onu_id):
  session = get_mysql_session()
  start_time = update_time = session.execute('SELECT NOW();').scalar() - timedelta(minutes=1)
  logger.debug('find_onu_connection: start_time: {0}'.format(start_time))
  board_number = '12' if onu_id[0] == '1' else '14'
  checking_frequency = 4
  vlan_name = 'v{0}00-P{1}-PON{2}-CLIENTES-FIBRA'.format(onu_id[0:2], board_number, onu_id[1])
  tn_formated_pon_name = format_pon_name(vlan_name)
  while not one_day_has_passed(start_time, update_time):
    query_string = 'SELECT user, pass, sucess, CallingStationId FROM {0} WHERE CalledStationId = :vlanname ' \
                   'AND date > :updatetime ORDER BY date DESC;'.format(mysqldb_config.radius_postauth_table)
    users = session.execute(query_string, {'vlanname': vlan_name, 'updatetime': update_time}).fetchall()
    logger.debug(
      'find_onu_connection: query_string: {0} - vlanname: {1} - updatetime: {2}'.format(query_string, vlan_name,
                                                                                        update_time))
    update_time = session.execute('SELECT NOW();').scalar() - timedelta(minutes=1)
    logger.debug('find_onu_connection: users: {0}'.format(users))
    if len(users):
      with Telnet(telnet_config.ip, telnet_config.port) as tn:
        connect_su(tn)
        for user in users:
          if (
              onu_id_from_user := get_onu_id_by_mac_and_pon(tn, user['CallingStationId'],
                                                            tn_formated_pon_name)) == onu_id:
            logger.debug('find_onu_connection: onu_id_from_user: {0}'.format(onu_id_from_user))
            diagnostic = diagnose_connection(session, user)
            logger.debug('find_onu_connection: diagnostic: {0}'.format(diagnostic))
            if not diagnostic:
              times_tried = 1
              while not diagnostic or times_tried > 3:
                sleep(30)
                diagnostic = diagnose_connection(session, user)
                logger.debug('find_onu_connection: diagnostic: {0}'.format(diagnostic))
                times_tried = times_tried + 1
              if not diagnostic:
                user = session.execute(
                  'SELECT user, pass, sucess, CallingStationId FROM {0} WHERE user = :username ORDER BY date '
                  'DESC;'.format(mysqldb_config.radius_postauth_table), {'username': user['user']}).first()
                logger.debug('find_onu_connection: user: {0}'.format(user))
                if user['sucess'] == 0 and user['pass'] == session.execute(
                    'SELECT pass FROM {0} WHERE user = :username;'.format(mysqldb_config.login_table),
                    {'username': user['user']}):
                  reauthorize_user(session, user['user'])
                  diagnostic = 'erro, reinicie o roteador.'
                elif user['sucess'] == 0:
                  diagnostic = 'erro, senha do usuário errada.'
                else:
                  diagnostic = 'desconhecido.'
            user_data = {'username': user['user'], 'password': user['pass'], 'diagnostic': diagnostic}
            logger.debug('find_onu_connection: user_data: {0}'.format(user_data))
            return user_data
    logger.debug('find_onu_connection: sleep: {0}'.format(checking_frequency))
    sleep(checking_frequency)
    if checking_frequency < 120:
      checking_frequency = checking_frequency + checking_frequency
  return None
