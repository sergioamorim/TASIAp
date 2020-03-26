from argparse import ArgumentParser

from common.mysql_common import supply_mysql_session
from common.string_common import is_onu_id_valid
from common.telnet_common import supply_telnet_connection, str_to_telnet
from config import mysqldb_config
from logger import get_logger, Log

logger = get_logger(__name__)


@supply_mysql_session
def get_login_password(username, session=None):
  sql_query = 'SELECT pass FROM {0} WHERE user = :username;'.format(mysqldb_config.login_table)
  if login_password := session.scalar(sql_query, {'username': username}):
    return login_password.replace('=3F', '?')
  logger.error('get_login_password: password for user {0} not found').format(username)
  return None


def encode_login_password(password):
  return ''.join(map(lambda x: chr(x), map(lambda x: 158-ord(x), list(password))))


def get_encoded_login_password(username):
  if login_password := get_login_password(username):
    return encode_login_password(login_password)
  return None


def can_set_router_onu_username(onu_id, encoded_password):
  return is_onu_id_valid(onu_id) and encoded_password


def generate_cvlan(onu_id):
  if is_onu_id_valid(onu_id):
    return int(onu_id[:2] + '00')
  return None


def get_onu_number(onu_id):
  if is_onu_id_valid(onu_id):
    return int(onu_id[2:])
  return None


def get_pon_id(onu_id):
  if is_onu_id_valid(onu_id):
    return onu_id[1:2]
  return None


def get_board_id(onu_id):
  if is_onu_id_valid(onu_id):
    return '12' if onu_id[:1] == '1' else '14'
  return None


def get_onu_id(board_id, pon_id, onu_number):
  board_onu_id = '1' if board_id == '12' else '2'
  onu_onu_id = '{0}{1}'.format('0' if int(onu_number) < 10 else '', onu_number)
  return '{0}{1}{2}'.format(board_onu_id, pon_id, onu_onu_id)


@supply_telnet_connection
def set_router_onu_username_effective(board_id, pon_id, onu_number, cvlan, username, encoded_password, tn=None):
  telnet_command_string = 'set wancfg sl {0} {1} {2} ind 1 mode inter ty r {3} 0 nat en qos dis vlanm tag tvlan ' \
                          'dis 65535 65535 dsp pppoe pro dis {4} key:{5} null auto active en'.format(
                           board_id, pon_id, onu_number, cvlan, username, encoded_password)
  tn.write(str_to_telnet('cd epononu'))
  tn.read_until(b'Admin\\epononu# ', timeout=1)
  tn.write(str_to_telnet('cd qinq'))
  tn.read_until(b'Admin\\epononu\\qinq# ', timeout=1)
  tn.write(str_to_telnet(telnet_command_string))
  if 'failed' not in tn.read_until(b'Admin\\epononu\\qinq# ', timeout=1).decode('ascii'):
    return True
  logger.error('set_router_onu_username_effective: onu {0} not found'.format(get_onu_id(board_id, pon_id, onu_number)))
  return None


def set_router_onu_username(onu_id, username):
  encoded_password = get_encoded_login_password(username)
  if can_set_router_onu_username(onu_id, encoded_password):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number(onu_id)
    cvlan = generate_cvlan(onu_id)
    return set_router_onu_username_effective(board_id, pon_id, onu_number, cvlan, username, encoded_password)
  return None


@Log(logger)
def update_router_onu_config(onu_id, ssid=None, password=None, username=None):
  if username:
    return set_router_onu_username(onu_id, username)
  return None


def main():

  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser configurada')
  parser.add_argument('-s', '--ssid', dest='s', help='SSID a ser configurado', default=None)
  parser.add_argument('-p', '--password', dest='p', help='Senha do Wi-Fi a ser configurada', default=None)
  parser.add_argument('-u', '--username', dest='u', help='Usuário a ser configurado', default=None)
  args = parser.parse_args()

  if manage_result := update_router_onu_config(args.i, ssid=args.s, password=args.p, username=args.u):
    print(repr(manage_result))
    return 0

  return 1


if __name__ == '__main__':
  main()
