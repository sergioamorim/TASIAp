from argparse import ArgumentParser

from tasiap.common.mysql_common import supply_mysql_session
from tasiap.common.string_common import get_onu_id_from_cto_vlan_name, get_cto_name_from_cto_vlan_name, \
  get_vlan_id_from_cto_vlan_name
from tasiap.logger import Log, get_logger

logger = get_logger(__name__)


class Cto(object):

  def __init__(self, query_result):
    self.onu_id = get_onu_id_from_cto_vlan_name(query_result[0])
    self.vlan_id = get_vlan_id_from_cto_vlan_name(query_result[0])
    self.cto_name = get_cto_name_from_cto_vlan_name(query_result[0])
    self.last_connected = query_result[1] if len(query_result) > 1 else None

  def __hash__(self):
    return int(self.onu_id)

  def __eq__(self, other):
    return True if self.onu_id == other.onu_id else False

  def __lt__(self, other):
    if self.last_connected and not other.last_connected:
      return True
    if not self.last_connected and other.last_connected:
      return False
    if not self.last_connected and not other.last_connected:
      return self.onu_id < other.onu_id
    return True if self.last_connected < other.last_connected else False

  def __repr__(self):
    return '<Cto(onu_id={0!r},vlan_id={1!r},cto_name={2!r},last_connected={3!r})>'.format(self.onu_id, self.vlan_id,
                                                                                          self.cto_name,
                                                                                          self.last_connected)


@supply_mysql_session
def get_query_results_online(cto_name, session=None):
  clause = "SELECT DISTINCT CalledStationID FROM radius_acct WHERE CalledStationID LIKE :cto_name AND AcctStopTime " \
           "= '0000-00-00 00:00:00';"
  return session.execute(clause=clause, params={'cto_name': '%{cto_name}%'.format(cto_name=cto_name.replace(' ', '%'))})


@supply_mysql_session
def get_query_results_all(cto_name, session=None):
  clause = "SELECT CalledStationId, max(AcctStopTime) last_connected FROM radius_acct WHERE CalledStationId LIKE " \
           ":cto_name GROUP BY CalledStationId ORDER BY last_connected DESC;"
  return session.execute(clause=clause, params={'cto_name': '%{cto_name}%'.format(cto_name=cto_name.replace(' ', '%'))})


@supply_mysql_session
@Log(logger)
def find_cto_by_name(cto_name, session=None):
  query_results_all = list(get_query_results_all(cto_name, session=session))
  query_results_all.extend(list(get_query_results_online(cto_name, session=session)))
  ctos_list = [Cto(query_result) for query_result in sorted(query_results_all, reverse=True)]
  ctos = set(sorted(ctos_list, reverse=True))
  return ctos


def main():
  parser = ArgumentParser()
  parser.add_argument('-n', '--name', dest='n', help='Nome da CTO a ser buscada.')
  args = parser.parse_args()

  if args.n:
    print(repr(find_cto_by_name(args.n)))
    return 0

  print('Informe a CTO a ser buscada.')
  return 1


if __name__ == '__main__':
  main()
