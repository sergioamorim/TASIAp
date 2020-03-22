from argparse import ArgumentParser
from re import findall

from common.mysql_common import supply_mysql_session, reauthorize_user
from common.sqlite_common import find_onu_info, update_onu_info
from common.string_common import sanitize_cto_vlan_name, format_datetime, format_onu_state
from common.telnet_common import str_to_telnet, supply_telnet_connection
from config import mysqldb_config
from logger import Log, get_logger
from onu_id_from_serial import find_onu_by_serial
from user_from_onu import find_user_by_onu

logger = get_logger(__name__)


def get_onu_number(pon_mac_lookup):
  onu_number_pattern = 'OnuId:([0-9]*)'
  if onu_number := findall(onu_number_pattern, pon_mac_lookup):
    return onu_number[0]
  return None


@supply_telnet_connection
def get_onu_id_by_mac_and_pon(mac, pon, tn=None):
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'Admin\\gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_mac {0} lookup {1}'.format(pon, mac.replace(':', ''))))
  pon_mac_lookup = tn.read_until(b'Admin\\gponline# ', timeout=1).decode('ascii')
  if onu_number := get_onu_number(pon_mac_lookup):
    board_id = '1' if pon[5:7] == '12' else '2'
    return '{0}{1}{2}{3}'.format(board_id, pon[13:], '0' if int(onu_number) < 10 else '', onu_number)
  return None


@supply_telnet_connection
def get_onu_id_by_mac(mac, pon, tn=None):
  if pon:
    if onu_id := get_onu_id_by_mac_and_pon(mac, pon, tn=tn):
      return onu_id
  pon_list = get_pon_list(tn=tn)
  if pon:
    pon_list.remove(pon)
  for pon in pon_list:
    if onu_id := get_onu_id_by_mac_and_pon(mac, pon, tn=tn):
      return onu_id
  return ''


@supply_telnet_connection
def get_pon_list(tn=None):
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_auth all'))
  show_pon_auth_all = tn.read_until(b'Admin\\gponline# ', timeout=1).decode('ascii')
  pon_pattern = '(slot [0-9]* link [0-9]*) *,auth mode is physical id.'
  pon_list = findall(pon_pattern, show_pon_auth_all)
  return pon_list


def format_pon_name(vlan_name):
  if len(vlan_name) > 13 and vlan_name[5:7] == '-P' and vlan_name[9:13] == '-PON':
    return 'slot {0} link {1}'.format(vlan_name[7:9], vlan_name[13:14])
  return None


def check_connection_by_onu_id_same_serial(onu_info, onu_state):
  if user_from_onu_id := find_user_by_onu(str(onu_info['onu_id'])):
    update_onu_info(onu_info['onu_id'], serial=onu_info['serial'], username=user_from_onu_id)
    return 'Informação pode estar incorreta pois o usuário {0} está conectado através da ONU ID {1} com serial {2} e ' \
           'a ONU está {3}.'.format(user_from_onu_id, onu_info['onu_id'], onu_info['serial'],
                                    format_onu_state(onu_state))
  return 'Nenhum usuário foi encontrado conectado à ONU ID {0}, o serial continua sendo o mesmo ({1}) e ela está ' \
         '{2}.'.format(onu_info['onu_id'], onu_info['serial'], format_onu_state(onu_state))


def diagnose_onu_not_found(pon, query_result, cto_name, onu_id, onu_info):
  diagnostic_addition = ''
  if cto_name:
    return '\nUsuário está desconectado. Última conexão através da ONU da {0}.\nPossíveis problemas:\n- roteador ' \
           'desligado, travado ou desconectado da ONU;\n- ONU travada, sem sinal ou desligada. Verifique o sinal da ' \
           'ONU com o comando "/sinal {1}".'.format(cto_name, onu_id)
  elif pon:
    if onu_info:
      checked_id = False
      if onu_id_by_serial := find_onu_by_serial(onu_info['serial']):
        if onu_id_by_serial['onu_id'] == str(onu_info['onu_id']):
          diagnostic_second_addition = check_connection_by_onu_id_same_serial(onu_info, onu_id_by_serial['state'])
          checked_id = True
        else:
          if user_from_onu_id := find_user_by_onu(onu_id_by_serial['onu_id']):
            update_onu_info(int(onu_id_by_serial['onu_id']), serial=onu_info['serial'], username=user_from_onu_id)
            diagnostic_fourth_addition = 'O usuário {0} está conectado na ONU ID {1} de serial {2}.'.format(
              user_from_onu_id, onu_id_by_serial['onu_id'], onu_info['serial'])
          else:
            diagnostic_fourth_addition = 'Nenhum usuário foi encontrado conectado através da ONU ID {0} (serial ' \
                                         '{1}).'.format(onu_id_by_serial['onu_id'], onu_info['serial'])
          diagnostic_second_addition = 'A ONU de serial {0} agora está com o ID {1} e está {2}.\n{3}'.format(
            onu_info['serial'], onu_id_by_serial['onu_id'], format_onu_state(onu_id_by_serial['state']),
            diagnostic_fourth_addition)
      else:
        diagnostic_second_addition = 'A ONU de serial {0} não está autorizada.'
      diagnostic_addition = '\nONU utilizada anteriormente (informação de {0}):\n - Serial: {1}\n - ONU ID: ' \
                            '{2}\n{3}'.format(format_datetime(onu_info['last_update']), onu_info['serial'],
                                              onu_info['onu_id'], diagnostic_second_addition)
      if not checked_id:
        if user_from_onu_id := find_user_by_onu(str(onu_info['onu_id'])):
          diagnostic_addition = diagnostic_addition + '\nInformação pode estar incorreta pois o usuário {0} está ' \
                                                      'conectado através da ONU ID {1}.'.format(user_from_onu_id,
                                                                                                onu_info['onu_id'])
        else:
          diagnostic_addition = diagnostic_addition + '\nNenhum usuário foi encontrado conectado através da ONU ID ' \
                                                      '{0}.'.format(onu_info['onu_id'])
    board_number = '12' if query_result['CalledStationId'][1:2] == '1' else '14'
    return 'Usuário está desconectado. Última conexão através de FIBRA na Placa {0} PON {1}.\nPossíveis problemas:\n' \
           '- roteador desligado ou desconectado da ONU;\n- ONU travada, sem sinal ou desligada.' \
           '{2}'.format(board_number, query_result['CalledStationId'][2:3], diagnostic_addition)
  else:
    return 'Usuário não conecta por ONU.\nRede: {0}'.format(query_result['CalledStationId'])


def diagnose_login(session, query_result, username):
  if query_result['sucess'] == 0:
    if (login_result := session.execute('SELECT cliente_id, pass, enable FROM login WHERE user = :username;',
                                        {'username': username}).first()):
      if login_result['pass'] == query_result['pass']:
        if login_result['enable'] == 1:
          if client_status := session.execute('SELECT status FROM clientes WHERE id = :clientid;',
                                              {'clientid': login_result['cliente_id']}).scalar():
            if client_status == 1:
              reauthorize_user(session, username)
              return '\nUsuário não conectado. Roteador encontrado, usuário e senha corretos - reinicie o roteador.'
            elif client_status == 2:
              return '\nUsuário não conectado pois cliente está bloqueado por pendência financeira. Usuário e senha ' \
                     'corretos. '
            elif client_status == 0:
              return '\nUsuário não conectado pois cadastro do cliente está desativado. Usuário e senha corretos.'
            return '\nUsuário não conectado pois cliente está bloquado manualmente. Usuário e senha corretos.'
          return '\nErro. Cadastro do cliente não encontrado.'
        return '\nUsuário não conectado pois o login está desativado. Roteador encontrado, usuário e senha corretos.'
      return '\nUsuário não conectado. Roteador encontrado, senha incorreta.\nUsuário: {0}\nSenha correta: ' \
             '{1}\nSenha informada: {2}'.format(username, login_result['pass'], query_result['pass'])
    return '\nErro. Login não encontrado. Verifique o usuário e senha no roteador.'
  return '\nErro. Conexão do usuário não encontrada. Reinicie o roteador.'


def get_onu_from_connection(session, query_result, username, do_diagnose_login=False):
  diagnostic = ''
  pon = format_pon_name(query_result['CalledStationId'])
  cto_name = sanitize_cto_vlan_name(query_result['CalledStationId'])
  if onu_id := get_onu_id_by_mac(query_result['CallingStationId'], pon):
    if not cto_name:
      update_onu_info(int(onu_id), username=username)
    if do_diagnose_login:
      diagnostic = diagnose_login(session, query_result, username)
  else:
    onu_info = None
    if cto_name:
      onu_id = query_result['CalledStationId'][1:5]
    elif onu_info := find_onu_info(username=username):
      onu_id = str(onu_info['onu_id'])
    diagnostic = diagnose_onu_not_found(pon, query_result, cto_name, onu_id, onu_info)
  return {'onu_id': onu_id, 'cto_name': cto_name, 'diagnostic': diagnostic}


@supply_mysql_session
@Log(logger)
def find_onu_by_user(username, session=None):
  query_acct = "SELECT CallingStationId, CalledStationId FROM {0} WHERE UserName = :username ORDER BY AcctStartTime " \
               "DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
  query_postauth = "SELECT sucess, pass, CallingStationId, CalledStationId FROM {0} WHERE user = :username ORDER BY " \
                   "date DESC LIMIT 1;".format(mysqldb_config.radius_postauth_table)
  onu_info = {'onu_id': '', 'cto_name': '', 'diagnostic': ''}
  if query_result := session.execute(query_acct, {'username': username}).first():
    onu_info = get_onu_from_connection(session, query_result, username)
  elif query_result := session.execute(query_postauth, {'username': username}).first():
    onu_info = get_onu_from_connection(session, query_result, username, do_diagnose_login=True)
  return onu_info


def main():
  parser = ArgumentParser()
  parser.add_argument('-u', '--username', dest='u', help='Usuario a ser consultado.', default=None)
  args = parser.parse_args()

  if username := args.u:
    print(find_onu_by_user(username))
    return 0

  print('Informe o usuario.')
  return 1


if __name__ == '__main__':
  main()
