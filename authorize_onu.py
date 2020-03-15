from argparse import ArgumentParser
from re import findall
from subprocess import run
from telnetlib import Telnet

from common.string_common import is_int, is_vlan_id_valid
from common.telnet_common import str_to_telnet, connect_su
from config import telnet_config
from logger import get_logger

logger = get_logger(__name__)


class OnuDevice:
  phy_id = None
  pon = None
  onu_type = None
  number = None
  cvlan = None
  authorization_id = None

  def __init__(self, authorization_id, onu_type, phy_id, pon):
    self.phy_id = phy_id
    self.pon = pon
    self.onu_type = onu_type
    self.authorization_id = authorization_id

  def __repr__(self):
    return '<OnuDevice(phy_id={0},pon={1},onu_type={2},number={3},cvlan={4},authorization_id={5})>'.format(
      repr(self.phy_id), repr(self.pon), repr(self.onu_type), repr(self.number), repr(self.cvlan),
      repr(self.authorization_id))


class Pon:
  pon_id = None
  board = None
  last_authorized_onu_number = None

  def autoset_last_authorized_number(self):
    authorization_list = get_authorization_list(self)
    authorized_onu_quantity = int(findall('ITEM=([0-9]*)', authorization_list)[0])
    authorized_onu_numbers = findall('{0} *{1} *([0-9]*)'.format(self.board.board_id, self.pon_id), authorization_list)
    final_authorized_onu_number = int(authorized_onu_numbers[-1])
    if final_authorized_onu_number == authorized_onu_quantity:
      self.last_authorized_onu_number = authorized_onu_quantity
    else:
      self.last_authorized_onu_number = get_first_missing_number_precedent(authorized_onu_numbers)

  def __init__(self, pon_id, board):
    self.pon_id = pon_id
    self.board = board
    self.autoset_last_authorized_number()

  def __repr__(self):
    return '<Pon(pon_id={0},board={1},last_authorized_onu_number={2})>'.format(repr(self.pon_id), repr(self.board),
                                                                               repr(self.last_authorized_onu_number))


class Board:
  board_id = None

  def __init__(self, board_id):
    self.board_id = board_id

  def __repr__(self):
    return '<Board(board_id={0})>'.format(repr(self.board_id))


def get_next_value(tn):
  value = tn.read_until(b' ', timeout=10)
  while ' '.encode('ascii') in value[:-1] or ' '.encode('ascii') is value or '\n'.encode('ascii') in value[:-1]:
    value = tn.read_until(b' ', timeout=10)
  return value[:-1].decode('utf-8')


def connect_gpononu(tn):
  connect_su(tn)
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'gpononu# ', timeout=10)


def authorize_onu_effective(onu, cvlan):
  onu.number = onu.pon.last_authorized_onu_number + 1
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('set whitelist phy_addr address {0} password null action delete'.format(onu.phy_id)))
    tn.read_until(b'gpononu# ', timeout=10)
    tn.write(str_to_telnet('set authorization slot {0} link {1} type {2} onuid {3} phy_id {4}'.format(
      onu.pon.board.board_id, onu.pon.pon_id, onu.onu_type, onu.number, onu.phy_id)))
    tn.read_until(b'gpononu# ', timeout=10)
    tn.write(str_to_telnet('set whitelist phy_addr address {0} password null action add slot {1} link {2} onu {3} '
                           'type {4}'.format(onu.phy_id, onu.pon.board.board_id, onu.pon.pon_id, onu.number,
                                             onu.onu_type)))
  if cvlan:
    set_cvlan(onu, cvlan)
  return onu


def set_cvlan(onu, cvlan):
  onu_id = '{0}{1}{2}'.format('1' if onu.pon.board.board_id == '12' else '2', onu.pon.pon_id, onu.number)
  command_list = ['python3', 'onu_set_cvlan.py', '-i', '{0}'.format(onu_id), '-c', '{0}'.format(cvlan)]
  answer_string = run(command_list, capture_output=True).stdout.decode('utf-8')
  cvlan_commited = findall('_([0-9]{4})', answer_string)[0]
  onu.cvlan = int(cvlan_commited)


def get_first_missing_number_precedent(numbers_list):
  first_missing_number_precedent = 0
  for number in numbers_list:
    if int(number) != first_missing_number_precedent + 1:
      return first_missing_number_precedent
    first_missing_number_precedent = int(number)
  return first_missing_number_precedent


def find_onu_in_list(onu_list, auth_onu):
  if is_int(auth_onu):
    for onu in onu_list:
      if auth_onu == onu.authorization_id:
        return onu
  else:
    for onu in onu_list:
      if onu.phy_id == auth_onu:
        return onu
  return None


def get_discovery_list():
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('show discovery slot all link all'))
    discovery_list = tn.read_until(b'gpononu# ', timeout=10)
  return discovery_list.decode('ascii')


def get_authorization_list(pon):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('show authorization slot {0} link {1}'.format(pon.board.board_id, pon.pon_id)))
    authorization_list = tn.read_until(b'gpononu# ', timeout=10)
  return authorization_list.decode('ascii')


def get_onu_list(discovery_list):
  onu_list = []
  discovery_pon_list = findall('SLOT=([0-9]*) PON=([0-9]*) ,ITEM=([0-9]*)', discovery_list)
  for discovery_pon in discovery_pon_list:
    item_quantity = int(discovery_pon[2])
    if item_quantity:
      board_id = discovery_pon[0]
      pon_id = discovery_pon[1]
      board = Board(board_id)
      pon = Pon(pon_id, board)
      onu_raw_list = findall('(01.*),', discovery_list)[0]
      onu_tuple_list = findall('([0-9]*) *(.*?) *([0-9A-Z]{4}[0-9A-Fa-f]{8}) ', onu_raw_list)
      for onu_tuple in onu_tuple_list:
        onu_authorization_id = str(int(onu_tuple[0]))
        onu_type = onu_tuple[1]
        onu_phy_id = onu_tuple[2]
        onu = OnuDevice(onu_authorization_id, onu_type, onu_phy_id, pon)
        onu_list.append(onu)
  return onu_list


def authorize_onu(auth_onu=None, cvlan=None):
  discovery_list = get_discovery_list()
  onu_list = get_onu_list(discovery_list)
  if not len(onu_list):
    return None
  if not auth_onu:
    return onu_list
  onu = find_onu_in_list(onu_list, auth_onu)
  return authorize_onu_effective(onu, cvlan) if onu else 'ERROR'


def main():
  parser = ArgumentParser()
  parser.add_argument("-a", "--authorize-onu", dest="a",
                      help="Numero da ONU que deve ser autorizada da lista de ONUs disponiveis para autorizacao",
                      default=None)
  parser.add_argument("-c", "--cvlan", dest="c", help="CVLAN para configurar a ONU", default=None)
  args = parser.parse_args()

  auth_onu = str(args.a).replace(' ', '') if args.a else None
  cvlan = None
  if args.c:
    if is_vlan_id_valid(args.c) or args.c == 'cto':
      cvlan = str(args.c)
    else:
      logger.error('CVLAN invalida.')
      return 1
  print(repr(authorize_onu(auth_onu, cvlan)))


if __name__ == '__main__':
  main()
