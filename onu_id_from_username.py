#!/usr/bin/env python3.8
# coding=utf-8

import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telnetlib import Telnet
import mysqldb_config
import telnet_config
from telnet_common import connect_su, str_to_telnet, get_next_value
from string_common import sanitize_cto_vlan_name, is_int, is_onu_id_valid
from mysql_common import get_mysql_session, reauthorize_user

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
  if value == 'Admin\\gponline#':
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
  return ''

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

def diagnose_onu_not_found(pon, query_result, cto_name):
  if query_result['CalledStationId'][3:5] != '00' and is_int(query_result['CalledStationId'][3:5]):
    return '\nUsuário está desconectado. Última conexão através da ONU da {0}.\nPossíveis problemas:\n- roteador desligado, travado ou desconectado da ONU;\n- ONU travada, sem sinal ou desligada. Verifique o sinal da ONU com o comando "/sinal {1}".'.format(cto_name, query_result['CalledStationId'][1:5])
  elif pon:
    board_number = '12' if query_result['CalledStationId'][1:2] == '1' else '14'
    return 'Usuário está desconectado. Última conexão através de FIBRA na Placa {0} PON {1}.\nPossíveis problemas:\n- roteador desligado ou desconectado da ONU;\n- ONU travada, sem sinal ou desligada.'.format(board_number, query_result['CalledStationId'][2:3])
  else:
    return 'Usuário não conecta por ONU.\nRede: {0}'.format(query_result['CalledStationId'])

def diagnose_login(session, query_result, username):
  if query_result['sucess'] == 0:
    if (login_result := session.execute('SELECT cliente_id, pass, enable FROM login WHERE user = :username;', {'username': username}).first()):
      if login_result['pass'] == query_result['pass']:
        if login_result['enable'] == 1:
          if client_status := session.execute('SELECT status FROM clientes WHERE id = :clientid;', {'clientid': login_result['cliente_id']}).scalar():
            if client_status == 1:
              reauthorize_user(session, username)
              return '\nUsuário não conectado. Roteador encontrado, usuário e senha corretos - reinicie o roteador.'
            elif client_status == 2:
              return '\nUsuário não conectado pois cliente está bloqueado por pendência financeira. Usuário e senha corretos.'
            elif client_status == 0:
              return '\nUsuário não conectado pois cadastro do cliente está desativado. Usuário e senha corretos.'
            return '\nUsuário não conectado pois cliente está bloquado manualmente. Usuário e senha corretos.'
          return '\nErro. Cadastro do cliente não encontrado.'
        return '\nUsuário não conectado pois o login está desativado. Roteador encontrado, usuário e senha corretos.'
      return '\nUsuário não conectado. Roteador encontrado, senha incorreta.\nUsuário: {0}\nSenha correta: {1}\nSenha informada: {2}'.format(username, login_result['pass'], query_result['pass'])
    return '\nErro. Login não encontrado. Verifique o usuário e senha no roteador.'
  return '\nErro. Conexão do usuário não encontrada. Reinicie o roteador.'

def find_onu_by_user(username):
  onu_id = cto_name = diagnostic = ''
  session = get_mysql_session()
  query_acct = "SELECT CallingStationId, CalledStationId FROM {0} WHERE UserName = :username ORDER BY AcctStartTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
  query_postauth = "SELECT sucess, pass, CallingStationId, CalledStationId FROM {0} WHERE user = :username ORDER BY date DESC LIMIT 1;".format(mysqldb_config.radius_postauth_table)
  if (query_result := session.execute(query_acct, {'username': username}).first()):
    pon = format_pon_name(query_result['CalledStationId'])
    cto_name = sanitize_cto_vlan_name(query_result['CalledStationId'])
    if not (onu_id := get_onu_id_by_mac(query_result['CallingStationId'], pon)):
      if is_onu_id_valid(query_result['CalledStationId'][1:5]):
        onu_id = query_result['CalledStationId'][1:5]
      diagnostic = diagnose_onu_not_found(pon, query_result, cto_name)
  elif (query_result := session.execute(query_postauth, {'username': username}).first()):
    pon = format_pon_name(query_result['CalledStationId'])
    cto_name = sanitize_cto_vlan_name(query_result['CalledStationId'])
    if (onu_id := get_onu_id_by_mac(query_result['CallingStationId'], pon)):
      diagnostic = diagnose_login(session, query_result, username)
    else:
      if is_onu_id_valid(query_result['CalledStationId'][1:5]):
        onu_id = query_result['CalledStationId'][1:5]
      diagnostic = diagnose_onu_not_found(pon, query_result, cto_name)
  session.close()
  return {'onu_id': onu_id, 'cto_name': cto_name, 'diagnostic': diagnostic}

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