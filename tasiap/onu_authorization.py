from re import findall

from tasiap.common.sqlite_common import update_onu_info
from tasiap.common.string_common import is_int
from tasiap.common.telnet_common import str_to_telnet, supply_telnet_connection
from tasiap.logger import Log, get_logger
from tasiap.snmp.onu_vlan import set_cvlan

logger = get_logger(__name__)


class AuthOnuDevice:
  phy_id = None
  pon = None
  onu_type = None
  number = None
  cvlan = None
  authorization_id = None

  def set_cvlan(self, cvlan):
    if result := set_cvlan(auth_onu_device=self, cvlan=cvlan):
      self.cvlan = result['cvlan']

  def __init__(self, pon, authorization_id=None, onu_type=None, phy_id=None, onu_tuple=None):
    self.phy_id = phy_id if phy_id else onu_tuple[2]
    self.pon = pon
    self.onu_type = onu_type if onu_type else format_onu_type(onu_tuple[1])
    self.authorization_id = authorization_id if authorization_id else str(int(onu_tuple[0]))

  def __repr__(self):
    return '<AuthOnuDevice(phy_id={0!r},pon={1!r},onu_type={2!r},number={3!r},cvlan={4!r},authorization_id={5!r})>'. \
            format(self.phy_id, self.pon, self.onu_type, self.number, self.cvlan, self.authorization_id)

  def __eq__(self, other):
    return (
      self.phy_id == other.phy_id and
      self.cvlan == other.cvlan and
      self.onu_type == other.onu_type and
      self.number == other.number and
      self.authorization_id == other.authorization_id and
      self.pon == other.pon
    )


def get_last_authorized_number(authorization_list):
  if board_and_pon := findall('show authorization slot ([0-9]*) link ([0-9]*)', authorization_list):
    board_id = board_and_pon[0][0]
    pon_id = board_and_pon[0][1]
    if authorized_onu_quantity := findall('ITEM=([0-9]*)', authorization_list):
      if authorized_onu_quantity := int(authorized_onu_quantity[0]):
        pattern = '{board_id} *{pon_id} *([0-9]*)'.format(board_id=board_id, pon_id=pon_id)
        authorized_onu_numbers = findall(pattern=pattern, string=authorization_list)
        final_authorized_onu_number = int(authorized_onu_numbers[-1])
        if final_authorized_onu_number == authorized_onu_quantity:
          return authorized_onu_quantity
        else:
          return get_first_missing_number_precedent(authorized_onu_numbers)
      return 0
    return None
  return None


class Pon:
  pon_id = None
  board = None
  last_authorized_onu_number = None

  @supply_telnet_connection
  def autoset_last_authorized_number(self, tn=None):
    authorization_list = get_authorization_list(self, tn=tn)
    self.last_authorized_onu_number = get_last_authorized_number(authorization_list=authorization_list)

  @supply_telnet_connection
  def __init__(self, pon_id, board=None, board_id=None, tn=None):
    self.pon_id = pon_id
    self.board = board if board else Board(board_id=board_id)
    self.autoset_last_authorized_number(tn=tn)

  def __repr__(self):
    return '<Pon(pon_id={0!r},board={1!r},last_authorized_onu_number={2!r})>'.format(self.pon_id, self.board,
                                                                                     self.last_authorized_onu_number)

  def __eq__(self, other):
    return (
      self.pon_id == other.pon_id and
      self.last_authorized_onu_number == other.last_authorized_onu_number and
      self.board == other.board
    )


class Board:
  board_id = None

  def __init__(self, board_id):
    self.board_id = board_id

  def __repr__(self):
    return '<Board(board_id={0!r})>'.format(self.board_id)

  def __eq__(self, other):
    return self.board_id == other.board_id


@supply_telnet_connection
def authorize_onu_effective(onu, cvlan, tn=None):
  onu.number = onu.pon.last_authorized_onu_number + 1
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ', timeout=10)
  tn.write(str_to_telnet('set whitelist phy_addr address {0} password null action delete'.format(onu.phy_id)))
  tn.read_until(b'Admin\\gpononu# ', timeout=10)
  tn.write(str_to_telnet('set authorization slot {0} link {1} type {2} onuid {3} phy_id {4}'.format(
    onu.pon.board.board_id, onu.pon.pon_id, onu.onu_type, onu.number, onu.phy_id)))
  tn.read_until(b'Admin\\gpononu# ', timeout=10)
  tn.write(str_to_telnet('set whitelist phy_addr address {0} password null action add slot {1} link {2} onu {3} '
                         'type {4}'.format(onu.phy_id, onu.pon.board.board_id, onu.pon.pon_id, onu.number,
                                           onu.onu_type)))
  if cvlan:
    onu.set_cvlan(cvlan)
  update_onu_info(auth_onu_device=onu)
  return onu


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


@supply_telnet_connection
def get_discovery_list(tn=None):
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ', timeout=10)
  tn.write(str_to_telnet('show discovery slot all link all'))
  discovery_list = tn.read_until(b'Admin\\gpononu# ', timeout=10)
  return discovery_list.decode('ascii')


@supply_telnet_connection
def get_authorization_list(pon, tn=None):
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ', timeout=10)
  tn.write(str_to_telnet('show authorization slot {0} link {1}'.format(pon.board.board_id, pon.pon_id)))
  authorization_list = tn.read_until(b'Admin\\gpononu# ', timeout=10)
  return authorization_list.decode('ascii')


def format_onu_type(onu_type):
  if onu_type[:2] == 'AN':
    return onu_type[2:].lower()
  return onu_type.lower()


@supply_telnet_connection
def get_onu_list(discovery_list, tn=None):
  onu_list = []
  discovery_pon_list = findall('SLOT=([0-9]*) PON=([0-9]*) ,ITEM=([0-9]*)', discovery_list)
  for discovery_pon in discovery_pon_list:
    item_quantity = int(discovery_pon[2])
    if item_quantity:
      board_id = discovery_pon[0]
      pon_id = discovery_pon[1]
      pon = Pon(pon_id=pon_id, board_id=board_id, tn=tn)

      onu_tuples_list = onu_tuples(
        board_id=board_id,
        discovery_list=discovery_list,
        item_quantity=item_quantity,
        pon_id=pon_id
      )

      for onu_tuple in onu_tuples_list:
        onu = AuthOnuDevice(onu_tuple=onu_tuple, pon=pon)
        onu_list.append(onu)
  return onu_list


def onu_tuples(board_id, discovery_list, item_quantity, pon_id):
  onus_textual = onus_from_pon_textual(
    board_id=board_id,
    discovery_list=discovery_list,
    item_quantity=item_quantity,
    pon_id=pon_id
  )
  return onu_tuples_found(onus_textual)


def onu_tuples_found(onus_list_textual):
  return findall('([0-9]*) *(.*?) *([0-9A-Z]{4}[0-9A-Fa-f]{8}) ', onus_list_textual)


def onus_from_pon_textual(board_id, discovery_list, item_quantity, pon_id):
  pon_discovery_textual_pattern = onus_from_pon_textual_pattern(
    board_id=board_id,
    item_quantity=item_quantity,
    pon_id=pon_id
  )
  return onus_from_pon_textual_found(
    discovery_list=discovery_list,
    pon_discovery_textual_pattern=pon_discovery_textual_pattern
  )


def onus_from_pon_textual_found(discovery_list, pon_discovery_textual_pattern):
  return findall(
    pattern=pon_discovery_textual_pattern,
    string=discovery_list
  )[0][0].replace('\r', '')


def onus_from_pon_textual_pattern(board_id, item_quantity, pon_id):
  return str(
    'SLOT={board_id} PON={pon_id} ,ITEM={item_quantity}'
    '[-\nA-Z\\s_,]*'  # junk from header
    '([-\n\r\\s_,A-Za-z0-9]*)'  # the actual onu list is here
    '(-{{5}}|Admin)'  # stop condition
  ).format(board_id=board_id, pon_id=pon_id, item_quantity=item_quantity)


@supply_telnet_connection
@Log(logger)
def authorize_onu(auth_onu=None, cvlan=None, tn=None):
  discovery_list = get_discovery_list(tn=tn)
  onu_list = get_onu_list(discovery_list=discovery_list, tn=tn)
  if not len(onu_list):
    return None
  if not auth_onu:
    return onu_list
  if onu := find_onu_in_list(onu_list=onu_list, auth_onu=auth_onu):
    return authorize_onu_effective(onu=onu, cvlan=cvlan, tn=tn)
  return 'ERROR'
