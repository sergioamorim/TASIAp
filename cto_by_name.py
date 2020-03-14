from common.mysql_common import get_mysql_session
from common.string_common import sanitize_cto_vlan_name
from config import mysqldb_config
from logger import get_logger

logger = get_logger(__name__)


def find_cto_by_name(string_list):
  logger.debug('find_cto_by_name({0})'.format(string_list))
  session = get_mysql_session()
  sql_query_string_all = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%';".format(
    mysqldb_config.radius_acct_table, '%'.join(string_list))
  query_results_all = session.execute(sql_query_string_all)
  sql_query_string_online = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%' AND " \
                            "AcctStopTime = '0000-00-00 00:00:00';".format(mysqldb_config.radius_acct_table,
                                                                           '%'.join(string_list))
  query_results_online = session.execute(sql_query_string_online)
  ctos_found = []
  for query_result in query_results_all:
    cto_name = sanitize_cto_vlan_name(query_result['CalledStationID'])
    if query_result['CalledStationID'] in query_results_online:
      ctos_found.append(cto_name)
    else:
      ctos_found.append('*{0} (clientes offline)'.format(cto_name))
  session.close()
  logger.info('find_cto_by_name({0}): {1}'.format(string_list, ctos_found))
  return ctos_found
