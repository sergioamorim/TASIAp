from argparse import ArgumentParser
from re import findall

from tasiap.common.mysql_common import supply_mysql_session
from tasiap.common.sqlite_common import update_onu_info
from tasiap.common.string_common import sanitize_cto_vlan_name, is_onu_id_valid, get_board_id, get_pon_id, \
  get_onu_number_from_id
from tasiap.common.telnet_common import str_to_telnet, supply_telnet_session
from tasiap.logger import Log, get_logger

logger = get_logger(__name__)


def is_cto_id(session, onu_id):
  clause = "SELECT DISTINCT CalledStationID FROM radius_acct WHERE AcctStopTime = '0000-00-00 00:00:00' AND " \
           "CalledStationID LIKE :onu_id ORDER BY AcctStartTime DESC LIMIT 1;"
  if cto_vlan_name := session.execute(clause=clause, params={'onu_id': '%{onu_id}%'.format(onu_id=onu_id)}).scalar():
    return sanitize_cto_vlan_name(cto_vlan_name)
  if onu_id[:1] == '1':
    board = '12'
  else:
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:]
  cto_like_name = 'P{0}-PON{1}-ONU{2}'.format(board, pon, onu_number)
  clause = "SELECT DISTINCT CalledStationID FROM radius_acct WHERE AcctStopTime = '0000-00-00 00:00:00' AND " \
           "CalledStationID LIKE :cto_like_name ORDER BY AcctStartTime DESC LIMIT 1;"
  params = {'cto_like_name': '%{cto_like_name}%'.format(cto_like_name=cto_like_name)}
  if cto_vlan_name := session.execute(clause=clause, params=params).scalar():
    return sanitize_cto_vlan_name(cto_vlan_name)
  return None


def is_offline_cto_id(session, onu_id):
  clause = "SELECT DISTINCT CalledStationID FROM radius_acct WHERE CalledStationID LIKE :onu_id ORDER BY " \
           "AcctStopTime DESC LIMIT 1;"
  if cto_vlan_name := session.execute(clause=clause, params={'onu_id': '%{onu_id}%'.format(onu_id=onu_id)}).scalar():
    return '{0} (offline)'.format(sanitize_cto_vlan_name(cto_vlan_name))
  if onu_id[:1] == '1':
    board = '12'
  else:
    board = '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:]
  cto_like_name = 'P{0}-PON{1}-ONU{2}'.format(board, pon, onu_number)
  clause = "SELECT DISTINCT CalledStationID FROM radius_acct WHERE CalledStationID LIKE :cto_like_name ORDER BY " \
           "AcctStopTime DESC LIMIT 1;"
  params = {'cto_like_name': '%{cto_like_name}%'.format(cto_like_name=cto_like_name)}
  if cto_vlan_name := session.execute(clause=clause, params=params).scalar():
    return '{0} (offline)'.format(sanitize_cto_vlan_name(cto_vlan_name))
  return None


def get_mac_list(show_pon_mac, onu_number):
  return findall(
    pattern=str(  # \t <MAC>\t Vid:<vlan>\t OnuId:<onu_number>\n
      '\\t([0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}})\\t *Vid:[0-9]*\\t '
      '*OnuId:{onu_number}\\n'
    ).format(onu_number=onu_number),
    string=show_pon_mac
  )


@supply_telnet_session
def get_mac_list_from_onu_id(onu_id, telnet=None):
  board = '12' if onu_id[:1] == '1' else '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
  telnet.write(str_to_telnet('cd gponline'))
  telnet.read_until(b'Admin\\gponline# ', timeout=1)
  telnet.write(str_to_telnet('show pon_mac slot {0} link {1}'.format(board, pon)))
  show_pon_mac = telnet.read_until(b'Admin\\gponline# ', timeout=1).decode('ascii')
  return get_mac_list(show_pon_mac, onu_number)


@supply_mysql_session
@Log(logger)
def find_user_by_onu(onu_id, session=None):
  if cto := is_cto_id(session, onu_id):
    return cto
  if mac_list := get_mac_list_from_onu_id(onu_id):
    username_list = []
    for mac in mac_list:
      sql_query_string = "SELECT DISTINCT UserName FROM radius_acct WHERE CallingStationID = :mac ORDER BY " \
                         "AcctStartTime DESC LIMIT 1;"
      if username := session.execute(sql_query_string, {'mac': mac}).scalar():
        username_list.append(username)
    if username_list:
      if len(username_list) == 1:
        update_onu_info(onu_id=onu_id, username=username_list[0])
      usernames = ' '.join(username_list)
      return usernames
  elif cto := is_offline_cto_id(session, onu_id):
    return cto
  return None


def interactive_interface():
  onu_id = True
  while onu_id:
    onu_id = input('ONU ID: ')
    if is_onu_id_valid(onu_id=onu_id):
      if username := find_user_by_onu(onu_id):
        board_id = get_board_id(onu_id=onu_id)
        pon_id = get_pon_id(onu_id=onu_id)
        onu_number = get_onu_number_from_id(onu_id=onu_id)
        string_format = 'P{board_id} PON{pon_id} ONU{leading_zero}{onu_number} CLIENTE {username}'
        leading_zero = '0' if int(onu_number) < 10 else ''
        string_filled_out = string_format.format(board_id=board_id, pon_id=pon_id, leading_zero=leading_zero,
                                                 onu_number=onu_number, username=username.upper())
        print(string_filled_out)
      else:
        print('Not found.')
    elif onu_id == 'exit' or onu_id == 'quit':
      onu_id = None
    else:
      print('Invalid ONU ID.')
  return 0


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ONU id to find the username from the user connected to it',
                      default=None)
  args = parser.parse_args()

  if onu_id := args.i:
    if is_onu_id_valid(onu_id):
      print(find_user_by_onu(onu_id))
      return 0
    print('ID da ONU inválido.')
    return 1
  return interactive_interface()


if __name__ == '__main__':
  main()
