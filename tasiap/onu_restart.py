from tasiap.common.string_common import is_onu_id_valid, onu_address
from tasiap.common.telnet_common import supply_telnet_session
from tasiap.logger import Log, get_logger

logger = get_logger(__name__)


@supply_telnet_session
def restart_onu_effective(current_onu_address, telnet=None):
  telnet.write(b'cd gpononu\n')
  telnet.read_until(b'gpononu# ')
  telnet.write(
    'reset slot {board_id} link {pon_id} onulist {onu_number}\n'
    ''.format(
      board_id=current_onu_address['board_id'],
      pon_id=current_onu_address['pon_id'],
      onu_number=current_onu_address['onu_number']
    ).encode('ascii')
  )
  if result := telnet.read_until(b'gpononu# '):
    return result.decode('ascii')
  return None


@supply_telnet_session
def restart_onu(current_onu_address, telnet=None):
  if result := restart_onu_effective(current_onu_address, telnet=telnet):
    if 'no onu satisfy the list' in result:
      return 'not found'
    elif 'reset onu ok' in result:
      return 'done'
    else:
      return 'error'
  return None


@Log(logger)
def restart_onu_by_id(onu_id):
  if is_onu_id_valid(onu_id=onu_id):
    return restart_onu(current_onu_address=onu_address(onu_id=onu_id))

  logger.error(msg='restart_onu_by_id: invalid onu id ({onu_id!r})'.format(onu_id=onu_id))
  return None
