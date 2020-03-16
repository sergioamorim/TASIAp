from argparse import ArgumentParser

from common.mysql_common import get_mysql_session
from common.sqlite_common import find_onu_info
from common.string_common import get_enable_emoji, get_status_emoji, sanitize_cto_vlan_name, format_datetime
from config import mysqldb_config
from logger import get_logger

logger = get_logger(__name__)


def get_login_info(session, username):
  login_query_string = 'SELECT nome, endereco, numero, status, pass, ip, groupname, enable, info FROM {0} INNER JOIN ' \
                       '{1} ON cliente_id = clientes.id WHERE user = :username;'.format(mysqldb_config.clientes_table,
                                                                                        mysqldb_config.login_table)
  return session.execute(login_query_string, {'username': username}).first()


def get_connection_info(session, username):
  radius_acct_query_string = 'SELECT FramedIPAddress, CalledStationId, AcctStartTime, AcctStopTime FROM {0} WHERE ' \
                             'UserName = :username ORDER BY AcctStartTime DESC LIMIT 1;'.format(
                              mysqldb_config.radius_acct_table)
  return session.execute(radius_acct_query_string, {'username': username}).first()


def format_onu_info(onu_info):
  if not onu_info:
    return ''
  return '\nONU ID: {0} Serial: {1} (informações de {2})'.format(onu_info['onu_id'], onu_info['serial'],
                                                                 format_datetime(onu_info['last_update']))


def format_connection_info(username, connection_info):
  if not connection_info:
    return 'Usuário nunca conectou por PPPoE.'

  if not connection_info['AcctStopTime']:
    connection_status = 'Conectado desde: {0}\nIP: {1}'.format(format_datetime(connection_info['AcctStartTime']),
                                                               connection_info['FramedIPAddress'])
  else:
    connection_status = 'Desconectado.\nÚltima conexão: {0} a {1}'.format(
      format_datetime(connection_info['AcctStartTime']), connection_info['AcctStopTime'])

  if cto_name := sanitize_cto_vlan_name(connection_info['CalledStationId']):
    return 'Conexão por cabo na ONU da {0}.\n{1}'.format(cto_name, connection_status)
  if len(connection_info['CalledStationId']) == 29 and connection_info['CalledStationId'][-5:] == 'FIBRA':
    onu_info = find_onu_info(username=username)
    return 'Conexão por FIBRA na placa {0} PON {1}.{2}\n{3}'.format(connection_info['CalledStationId'][7:9],
                                                                    connection_info['CalledStationId'][13:14],
                                                                    format_onu_info(onu_info), connection_status)
  return 'Conexão através da VLAN {0}.\n{1}'.format(connection_info['CalledStationId'], connection_status)


def format_login_info(username, login_info, connection_info=None):
  ip = 'IP reservado: {0}\n'.format(login_info['ip']) if login_info['ip'] else ''
  aditional_info = 'Informações adicionais: {0}\n'.format(login_info['info']) if login_info['info'] else ''
  enable = 'sim' if login_info['enable'] else 'não'
  login_info_string = '{0} Login ativo: {1}\nSenha: {2}\n{3}Plano: {4}\n{5}{6} Nome: {7}\nEndereço: {8}, {9}\n{10}'. \
                      format(get_enable_emoji(login_info['enable']), enable, login_info['pass'], ip,
                             login_info['groupname'], aditional_info, get_status_emoji(login_info['status']),
                             login_info['nome'], login_info['endereco'], login_info['numero'],
                             format_connection_info(username, connection_info))
  return login_info_string


def find_login_info(username):
  logger.debug('find_login_info({0})'.format(repr(username)))
  session = get_mysql_session()
  if login_info := get_login_info(session, username):
    formatted_login_info = format_login_info(username, login_info, get_connection_info(session, username))
    logger.debug('find_login_info({0}): {1}'.format(repr(username), repr(formatted_login_info)))
    return formatted_login_info
  logger.debug('find_login_info({0}): can not find login info'.format(repr(username)))
  return None


def main():
  parser = ArgumentParser()
  parser.add_argument('-u', '--username', dest='u', help='Usuário a ser consultado.', default=None)
  args = parser.parse_args()

  if username := args.u:
    print(find_login_info(username))
    return 0

  print('Informe o usuário a ser consutado.')
  return 1


if __name__ == '__main__':
  main()