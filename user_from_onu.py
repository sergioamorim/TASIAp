from argparse import ArgumentParser
from re import findall

from common.mysql_common import supply_mysql_session
from common.sqlite_common import update_onu_info
from common.string_common import sanitize_cto_vlan_name, is_onu_id_valid
from common.telnet_common import str_to_telnet, supply_telnet_connection
from config import mysqldb_config
from logger import Log, get_logger

logger = get_logger(__name__)


def is_cto_id(session, onu_id):
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE AcctStopTime = '0000-00-00 00:00:00' AND " \
                     "CalledStationID LIKE '%{1}%' ORDER BY AcctStartTime DESC LIMIT " \
                     "1;".format(mysqldb_config.radius_acct_table, onu_id)
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


def get_mac_list(show_pon_mac, onu_number):
  mac_pattern = '\\t([0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}}:[0-9A-F]{{2}})\\t *Vid:[' \
                '0-9]*\\t *OnuId:{0}\\n'.format(onu_number)
  return findall(mac_pattern, show_pon_mac)


@supply_telnet_connection
def get_mac_list_from_onu_id(onu_id, tn=None):
  board = '12' if onu_id[:1] == '1' else '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'Admin\\gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_mac slot {0} link {1}'.format(board, pon)))
  show_pon_mac = tn.read_until(b'Admin\\gponline# ', timeout=1).decode('ascii')
  return get_mac_list(show_pon_mac, onu_number)


@supply_mysql_session
@Log(logger)
def find_user_by_onu(onu_id, session=None):
  if cto := is_cto_id(session, onu_id):
    return cto
  if mac_list := get_mac_list_from_onu_id(onu_id):
    username_list = []
    for mac in mac_list:
      sql_query_string = "SELECT DISTINCT UserName FROM {0} WHERE CallingStationID = :mac ORDER BY AcctStartTime " \
                         "DESC LIMIT 1;".format(mysqldb_config.radius_acct_table)
      if username := session.execute(sql_query_string, {'mac': mac}).scalar():
        username_list.append(username)
    if username_list:
      if len(username_list) == 1:
        update_onu_info(int(onu_id), username=username_list[0])
      usernames = ' '.join(username_list)
      return usernames
  elif cto := is_offline_cto_id(session, onu_id):
    return cto
  return None


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
  print('Informe o ID da ONU.')
  return 1


if __name__ == '__main__':
  main()
