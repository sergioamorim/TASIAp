from common.mysql_common import get_mysql_session
from common.string_common import sanitize_cto_vlan_name
from config import mysqldb_config
from logger import get_logger

logger = get_logger(__name__)


def find_cto_by_name(string_list):
  logger.debug('find_cto_by_name({0})'.format(string_list))
  session = get_mysql_session()
  sql_query_string = "SELECT DISTINCT CalledStationID FROM {0} WHERE CalledStationID LIKE '%{1}%' ORDER BY " \
                     "AcctStartTime DESC LIMIT 1;".format(mysqldb_config.radius_acct_table, '%'.join(string_list))
  query_results = session.execute(sql_query_string)
  ctos_found = []
  for query_result in query_results:
    ctos_found.append(sanitize_cto_vlan_name(query_result['CalledStationID']))
  session.close()
  logger.info('find_cto_by_name({0}): {1}'.format(string_list, ctos_found))
  return ctos_found
