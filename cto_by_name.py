from re import findall

from common.mysql_common import get_mysql_session
from common.string_common import sanitize_cto_vlan_name, format_datetime
from config import mysqldb_config
from logger import get_logger

logger = get_logger(__name__)


def get_cto_ids(cto_name):
  return findall('([0-9]{4})', cto_name)


def remove_cto_duplicates(cto_names):
  new_cto_names = []
  cropped_new_cto_names = []
  for cto_name in sorted(cto_names, key=len, reverse=True):
    if len(cto_name) > 28:
      new_cto_names.append(cto_name)
      cropped_new_cto_names.append(cto_name[:28])
      cto_names.remove(cto_name)
  for cto_name in cto_names:
    if cto_name not in cropped_new_cto_names:
      new_cto_names.append(cto_name)
  return new_cto_names


def get_query_results_online(session, string_list):
  sql_query_string_online = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%' AND " \
                            "AcctStopTime = '0000-00-00 00:00:00';".format(mysqldb_config.radius_acct_table,
                                                                           '%'.join(string_list))
  return session.execute(sql_query_string_online)


def get_query_results_all(session, string_list):
  sql_query_string_all = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%'".format(
    mysqldb_config.radius_acct_table, '%'.join(string_list))
  return session.execute(sql_query_string_all)


def get_cto_last_online(session, cto_vlan_name):
  sql_query_string = 'SELECT AcctStopTime FROM {0} WHERE CalledStationId = :ctovlanname ORDER BY AcctStopTime DESC ' \
                     'LIMIT 1'.format(mysqldb_config.radius_acct_table)
  return session.execute(sql_query_string, {'ctovlanname': cto_vlan_name}).scalar()


def find_cto_by_name(string_list):
  logger.debug('find_cto_by_name({0})'.format(string_list))
  session = get_mysql_session()
  query_results_all = get_query_results_all(session, string_list)
  query_results_online = get_query_results_online(session, string_list)
  ctos_found = []
  ctos_included = []
  for query_result in query_results_online:
    cto_name = sanitize_cto_vlan_name(query_result['CalledStationID'])
    ctos_included.extend(get_cto_ids(cto_name))
    ctos_found.append(cto_name)
  ctos_found = remove_cto_duplicates(ctos_found)
  offline_ctos = []
  for query_result in query_results_all:
    cto_name = sanitize_cto_vlan_name(query_result['CalledStationID'])
    cto_ids = get_cto_ids(cto_name)
    included = False
    for cto_id in cto_ids:
      if cto_id in ctos_included:
        included = True
    if not included:
      last_online = get_cto_last_online(session, query_result['CalledStationID'])
      offline_ctos.append({'cto_name': cto_name, 'last_online': last_online})
  for cto_dict in sorted(offline_ctos, key=lambda cto: cto['last_online'], reverse=True):
    last_online = format_datetime(cto_dict['last_online'])
    ctos_found.append('*{0} (clientes offline - {1})'.format(cto_dict['cto_name'], last_online))
  session.close()
  logger.info('find_cto_by_name({0}): {1}'.format(string_list, ctos_found))
  return ctos_found
