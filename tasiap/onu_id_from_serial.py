from re import findall

from tasiap.common.telnet_common import supply_telnet_session
from tasiap.logger import Log, get_logger

logger = get_logger(__name__)


@supply_telnet_session
@Log(logger)
def find_onu_by_serial(serial, telnet=None):
  if onu_state := onu_status_from_phy_id(
    phy_id=serial,
    current_authorization_table=authorization_table(telnet=telnet)
  ):
    return {
      'onu_id': onu_id_from_address(onu_address=onu_state['onu_address']),
      'state': onu_state['state']
    }
  return None


@supply_telnet_session
def authorization_table(telnet=None):
  telnet.write(b'cd gpononu\n')
  telnet.read_until(b'gpononu# ')
  telnet.write(b'show authorization slot all link all\n')
  if result := telnet.read_until(b'gpononu# '):
    return result.decode('ascii')
  return None


def onu_status_from_phy_id(phy_id, current_authorization_table):
  if onu_state := findall(
    pattern='([0-9]{{2}}) +([1-8]) +([0-9]+) +.* +A +(u?p?d?n?) +{phy_id}'.format(phy_id=phy_id),
    string=current_authorization_table
  ):
    return {
      'onu_address': {
        'board_id': onu_state[0][0],
        'pon_id': onu_state[0][1],
        'onu_number': onu_state[0][2]
      },
      'state': onu_state[0][3]
    }
  return None


def onu_id_from_address(onu_address):
  return '{board_id}{pon_id}{onu_number}'.format(
    board_id='1' if onu_address['board_id'] == '12' else '2',
    pon_id=onu_address['pon_id'],
    onu_number=onu_address['onu_number'].zfill(2)
  )
