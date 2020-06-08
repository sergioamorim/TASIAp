from datetime import timedelta
from time import sleep

from common.mysql_common import supply_mysql_session, reauthorize_user
from common.sqlite_common import update_onu_info
from common.telnet_common import supply_telnet_connection
from logger import get_logger
from onu_id_from_username import get_onu_id_by_mac_and_pon, format_pon_name

logger = get_logger(__name__)


def one_day_has_passed(start_time, actual_time):
  return actual_time - start_time > timedelta(days=1)


def diagnose_fail(session, user):
  if result := session.execute(clause='SELECT user, pass FROM login WHERE user = :username;',
                               params={'username': user['user']}).first():
    if result['pass']:
      if result['pass'] == user['pass']:
        return diagnose_account(session, user)
      return 'erro, senha do usuário errada.\nSenha recebida: {0}\nSenha correta: {1}'.format(user['pass'],
                                                                                              result['pass'])
    return 'erro, usuário sem senha de login cadastrada no sistema.'
  return 'erro, não existe login com esse usuário.'


def diagnose_account(session, user):
  query_string = 'SELECT cliente_id, enable FROM login WHERE user = :username;'
  if login := session.execute(query_string, {'username': user['user']}).first():
    if login['enable'] == 1:
      query_string = 'SELECT status FROM clientes WHERE id = :id;'
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
    return 'bloqueada, não existe login com esse usuário.'


def diagnose_connection(session, user):
  if not user['sucess']:
    return diagnose_fail(session, user)
  query_string = 'SELECT FramedIPAddress, AcctStopTime FROM radius_acct WHERE UserName = :username ORDER BY ' \
                 'AcctStartTime DESC;'
  if connection_info := session.execute(query_string, {'username': user['user']}).first():
    logger.debug('diagnose_connection: connection_info: {0}'.format(connection_info))
    if connection_info['FramedIPAddress'][4:6] == '66':
      return diagnose_account(session, user)
    else:
      if not connection_info['AcctStopTime']:
        return 'normal.\nIP: {0}'.format(connection_info['FramedIPAddress'])
      return 'conectou normalmente e em seguida desconectou.'
  return None


@supply_telnet_connection
@supply_mysql_session
def find_user_data(onu_id, users, session=None, tn=None):
  tn_formated_pon_name = format_pon_name(onu_id=onu_id)
  for user in users:
    if (onu_id_from_user := get_onu_id_by_mac_and_pon(user['CallingStationId'], tn_formated_pon_name, tn=tn)) == onu_id:
      update_onu_info(onu_id=onu_id, username=user['user'])
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
            clause='SELECT user, pass, sucess, CallingStationId FROM radius_postauth WHERE user = :username ORDER BY'
                   ' date DESC;', params={'username': user['user']}).first()
          logger.debug('find_onu_connection: user: {0}'.format(user))
          if not user['sucess']:
            diagnostic = diagnose_fail(session, user)
          else:
            diagnostic = 'desconhecido.'
      user_data = {'username': user['user'], 'password': user['pass'], 'diagnostic': diagnostic}
      logger.debug('find_onu_connection: user_data: {0}'.format(user_data))
      return user_data
    return None


@supply_mysql_session
def find_onu_connection(onu_id, session=None):
  start_time = update_time = session.execute('SELECT NOW();').scalar() - timedelta(minutes=1)
  logger.debug('find_onu_connection: start_time: {0}'.format(start_time))
  checking_frequency = 4
  board_number = '12' if onu_id[0] == '1' else '14'
  vlan_name = 'v{0}00-P{1}-PON{2}-CLIENTES-FIBRA'.format(onu_id[0:2], board_number, onu_id[1])
  while not one_day_has_passed(start_time, update_time):
    query_string = 'SELECT user, pass, sucess, CallingStationId FROM radius_postauth WHERE CalledStationId = ' \
                   ':vlanname AND date > :updatetime ORDER BY date DESC;'
    users = session.execute(query_string, {'vlanname': vlan_name, 'updatetime': update_time}).fetchall()
    logger.debug(
      'find_onu_connection: query_string: {0} - vlanname: {1} - updatetime: {2}'.format(query_string, vlan_name,
                                                                                        update_time))
    update_time = session.execute('SELECT NOW();').scalar() - timedelta(minutes=1)
    logger.debug('find_onu_connection: users: {0}'.format(users))
    if len(users):
      if user_data := find_user_data(onu_id, users, session=session):
        return user_data
    logger.debug('find_onu_connection: sleep: {0}'.format(checking_frequency))
    sleep(checking_frequency)
    if checking_frequency < 120:
      checking_frequency = checking_frequency + checking_frequency
  return None
