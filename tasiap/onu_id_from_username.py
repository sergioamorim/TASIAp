from re import findall

from tasiap.common.mysql_common import supply_mysql_session, reauthorize_user
from tasiap.common.sqlite_common import find_onu_info, update_onu_info
from tasiap.common.string_common import sanitize_cto_vlan_name, format_datetime, format_onu_state, get_board_id, \
  get_pon_id
from tasiap.common.telnet_common import supply_telnet_session
from tasiap.logger import Log, get_logger
from tasiap.onu_id_from_serial import find_onu_by_serial
from tasiap.user_from_onu import find_user_by_onu

logger = get_logger(__name__)


@Log(logger)
def get_onu_number(pon_mac_lookup):
  if onu_number := findall(pattern='OnuId:([0-9]*)', string=pon_mac_lookup):
    return onu_number[0]
  return None


@supply_telnet_session
def get_onu_id_by_mac_and_pon(mac, pon, telnet=None):
  telnet.write(b'cd gponline\n')
  telnet.read_until(b'Admin\\gponline# ', timeout=1)

  telnet.write(
    'show pon_mac {pon_address} lookup {mac}\n'.format(
      pon_address=pon,
      mac=mac.replace(':', '')
    ).encode('ascii')
  )

  pon_mac_lookup = telnet.read_until(b'Admin\\gponline# ', timeout=1).decode('ascii')
  if onu_number := get_onu_number(pon_mac_lookup=pon_mac_lookup):
    board_id = get_board_id(pon_name=pon)
    pon_id = get_pon_id(pon_name=pon)
    return '{board_id}{pon_id}{onu_number_leading_zero}{onu_number}'.format(
      board_id=board_id,
      pon_id=pon_id,
      onu_number_leading_zero='0' if int(onu_number) < 10 else '',
      onu_number=onu_number
    )
  return None


@supply_telnet_session
def get_onu_id_by_mac(mac, pon, telnet=None):
  if pon:
    if onu_id := get_onu_id_by_mac_and_pon(
      mac=mac,
      pon=pon,
      telnet=telnet
    ):
      return onu_id
  pon_list = get_pon_list(telnet=telnet)
  if pon:
    pon_list.remove(pon)
  for pon in pon_list:
    if onu_id := get_onu_id_by_mac_and_pon(
      mac=mac,
      pon=pon,
      telnet=telnet
    ):
      return onu_id
  return None


@supply_telnet_session
def get_pon_list(telnet=None):
  telnet.write(b'cd gponline\n')
  telnet.read_until(b'gponline# ')
  telnet.write(b'show pon_auth all\n')
  return findall(
    pattern='(slot [0-9]* link [0-9]*) *,auth mode is physical id.',
    string=telnet.read_until(b'Admin\\gponline# ').decode('ascii')
  )


def pon_address_from_onu_id(onu_id):
  return 'slot {board_id} link {pon_id}'.format(
    board_id=get_board_id(onu_id=onu_id),
    pon_id=get_pon_id(onu_id=onu_id)
  )


def board_id_and_pon_id_from_vlan_name(vlan_name):
  if board_id_and_pon_id_found := findall(
    pattern='.*-P([0-9]*)-PON([0-9]*)',
    string=vlan_name
  ):
    return {'board_id': board_id_and_pon_id_found[0][0], 'pon_id': board_id_and_pon_id_found[0][1]}
  return None


def pon_address_from_vlan_name(vlan_name):
  if board_id_and_pon_id := board_id_and_pon_id_from_vlan_name(vlan_name=vlan_name):
    return 'slot {board_id} link {pon_id}'.format(
      board_id=board_id_and_pon_id['board_id'],
      pon_id=board_id_and_pon_id['pon_id']
    )
  return None


def format_pon_name(vlan_name=None, onu_id=None):
  if onu_id:
    return pon_address_from_onu_id(onu_id=onu_id)
  if vlan_name:
    return pon_address_from_vlan_name(vlan_name=vlan_name)
  return None


def check_connection_by_onu_id_same_serial(onu_info, onu_state):
  if user_from_onu_id := find_user_by_onu(onu_id=str(onu_info['onu_id'])):
    update_onu_info(
      onu_id=onu_info['onu_id'],
      serial=onu_info['serial'],
      username=user_from_onu_id
    )
    return str(
      'Informação pode estar incorreta pois o usuário {username} está conectado através da ONU ID {onu_id} com serial '
      '{phy_id} e a ONU está {onu_state}.'
    ).format(
      username=user_from_onu_id,
      onu_id=onu_info['onu_id'],
      phy_id=onu_info['serial'],
      onu_state=format_onu_state(onu_state=onu_state)
    )
  return str(
    'Nenhum usuário foi encontrado conectado à ONU ID {onu_id}, o serial continua sendo o mesmo ({phy_id}) e ela está '
    '{onu_state}.'
  ).format(
    onu_id=onu_info['onu_id'],
    phy_id=onu_info['serial'],
    onu_state=format_onu_state(onu_state=onu_state)
  )


def diagnose_onu_not_found(pon, query_result, cto_name, onu_id, onu_info):
  diagnostic_addition = ''
  if cto_name:
    return str(
      '\nUsuário está desconectado. Última conexão através da ONU da {cto_name}.\n'
      'Possíveis problemas:\n'
      '- roteador desligado, travado ou desconectado da ONU;\n'
      '- ONU travada, sem sinal ou desligada. Verifique o sinal da ONU com o comando "/sinal {onu_id}".'
    ).format(
      cto_name=cto_name,
      onu_id=onu_id
    )
  elif pon:
    if onu_info:
      checked_id = False
      if onu_id_by_serial := find_onu_by_serial(serial=onu_info['serial']):
        if onu_id_by_serial['onu_id'] == str(onu_info['onu_id']):
          diagnostic_second_addition = check_connection_by_onu_id_same_serial(
            onu_info=onu_info,
            onu_state=onu_id_by_serial['state']
          )
          checked_id = True
        else:
          if user_from_onu_id := find_user_by_onu(onu_id=onu_id_by_serial['onu_id']):
            update_onu_info(
              onu_id=onu_id_by_serial['onu_id'],
              serial=onu_info['serial'],
              username=user_from_onu_id
            )
            diagnostic_fourth_addition = str(
              'O usuário {username} está conectado na ONU ID {onu_id} de serial {phy_id}.'
            ).format(
              username=user_from_onu_id,
              onu_id=onu_id_by_serial['onu_id'],
              phy_id=onu_info['serial']
            )
          else:
            diagnostic_fourth_addition = str(
              'Nenhum usuário foi encontrado conectado através da ONU ID {onu_id} (serial {phy_id}).'
            ).format(
              onu_id=onu_id_by_serial['onu_id'],
              phy_id=onu_info['serial']
            )
          diagnostic_second_addition = str(
            'A ONU de serial {phy_id} agora está com o ID {onu_id} e está {onu_state}.\n{diagnostic_fourth_addition}'
          ).format(
            phy_id=onu_info['serial'],
            onu_id=onu_id_by_serial['onu_id'],
            onu_state=format_onu_state(onu_state=onu_id_by_serial['state']),
            diagnostic_fourth_addition=diagnostic_fourth_addition
          )
      else:
        diagnostic_second_addition = str(
          'A ONU de serial {phy_id} não está autorizada.'
        ).format(phy_id=onu_info['serial'])
      diagnostic_addition = str(
        '\nONU utilizada anteriormente (informação de {update_time}):\n'
        ' - Serial: {phy_id}\n'
        ' - ONU ID: {onu_id}\n'
        '{diagnostic_second_addition}'
      ).format(
        update_time=format_datetime(onu_info['last_update']),
        phy_id=onu_info['serial'],
        onu_id=onu_info['onu_id'],
        diagnostic_second_addition=diagnostic_second_addition
      )
      if not checked_id:
        if user_from_onu_id := find_user_by_onu(onu_id=str(onu_info['onu_id'])):
          diagnostic_addition += str(
            '\nInformação pode estar incorreta pois o usuário {username} está conectado através da ONU ID {onu_id}.'
          ).format(
            username=user_from_onu_id,
            onu_id=onu_info['onu_id']
          )
        else:
          diagnostic_addition += str(
            '\nNenhum usuário foi encontrado conectado através da ONU ID {onu_id}.'
          ).format(onu_id=onu_info['onu_id'])
    board_id_and_pon_id = board_id_and_pon_id_from_vlan_name(vlan_name=query_result['CalledStationId'])
    return str(
      'Usuário está desconectado. Última conexão através de FIBRA na Placa {board_id} PON {pon_id}.\n'
      'Possíveis problemas:\n'
      '- roteador desligado ou desconectado da ONU;\n'
      '- ONU travada, sem sinal ou desligada.{diagnostic_addition}'.format(
        board_id=board_id_and_pon_id['board_id'],
        pon_id=board_id_and_pon_id['pon_id'],
        diagnostic_addition=diagnostic_addition
      )
    )
  else:
    return str(
      'Usuário não conecta por ONU.\n'
      'Rede: {vlan_name}'
    ).format(vlan_name=query_result['CalledStationId'])


def diagnose_login(session, query_result, username):
  if query_result['sucess'] == 0:
    if (login_result := session.execute(
      clause='SELECT cliente_id, pass, enable FROM login WHERE user = :username;',
      params={'username': username}).first()
    ):
      if login_result['pass'] == query_result['pass']:
        if login_result['enable'] == 1:
          if customer_status := session.execute(
            clause='SELECT status FROM clientes WHERE id = :customer_id;',
            params={'customer_id': login_result['cliente_id']}
          ).scalar():
            if customer_status == 1:
              reauthorize_user(session=session, username=username)
              return '\nUsuário não conectado. Roteador encontrado, usuário e senha corretos - reinicie o roteador.'
            elif customer_status == 2:
              return '\nUsuário não conectado pois cliente está bloqueado por pendência financeira.'
            elif customer_status == 0:
              return '\nUsuário não conectado pois cadastro do cliente está desativado.'
            return '\nUsuário não conectado pois cliente está bloqueado manualmente.'
          return '\nErro. Cadastro do cliente não encontrado.'
        return '\nUsuário não conectado pois o login está desativado.'
      return str(
        '\nUsuário não conectado. Roteador encontrado, senha incorreta.\n'
        'Usuário: {username}\n'
        'Senha correta: {correct_password}\n'
        'Senha informada: {given_password}'
      ).format(
        username=username,
        correct_password=login_result['pass'],
        given_password=query_result['pass']
      )
    return '\nErro. Login não encontrado. Verifique o usuário e senha no roteador.'
  return '\nErro. Conexão do usuário não encontrada. Reinicie o roteador.'


def get_onu_from_connection(session, query_result, username, do_diagnose_login=False):
  diagnostic = ''
  pon = format_pon_name(vlan_name=query_result['CalledStationId'])
  cto_name = sanitize_cto_vlan_name(cto_vlan_name=query_result['CalledStationId'])
  if onu_id := get_onu_id_by_mac(
    mac=query_result['CallingStationId'],
    pon=pon
  ):
    if not cto_name:
      update_onu_info(onu_id=onu_id, username=username)
    if do_diagnose_login:
      diagnostic = diagnose_login(
        session=session,
        query_result=query_result,
        username=username
      )
  else:
    onu_info = None
    if cto_name:
      onu_id = query_result['CalledStationId'][1:5]
    elif onu_info := find_onu_info(username=username):
      onu_id = str(onu_info['onu_id'])
    diagnostic = diagnose_onu_not_found(
      pon=pon,
      query_result=query_result,
      cto_name=cto_name,
      onu_id=onu_id,
      onu_info=onu_info
    )
  return {
    'onu_id': onu_id,
    'cto_name': cto_name,
    'diagnostic': diagnostic
  }


@supply_mysql_session
@Log(logger)
def find_onu_by_user(username, session=None):
  query_acct = str(
    'SELECT CallingStationId, CalledStationId FROM radius_acct WHERE UserName = :username ORDER BY AcctStartTime DESC '
    'LIMIT 1;'
  )
  query_postauth = str(
    'SELECT sucess, pass, CallingStationId, CalledStationId FROM radius_postauth WHERE user = :username ORDER BY date '
    'DESC LIMIT 1;'
  )
  onu_info = {'onu_id': '', 'cto_name': '', 'diagnostic': ''}
  if query_result := session.execute(
    clause=query_acct,
    params={'username': username}
  ).first():
    onu_info = get_onu_from_connection(
      session=session,
      query_result=query_result,
      username=username
    )
  elif query_result := session.execute(
    clause=query_postauth,
    params={'username': username}
  ).first():
    onu_info = get_onu_from_connection(
      session=session,
      query_result=query_result,
      username=username,
      do_diagnose_login=True
    )
  return onu_info
