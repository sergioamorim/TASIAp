from re import findall

from tasiap.common.string_common import get_pon_id, get_board_id, get_onu_number_from_id
from tasiap.common.telnet_common import supply_telnet_session
from tasiap.logger import Log, get_logger

logger = get_logger(__name__)


def get_signal_power(show_optic_module):
  signal_power_pattern = '\nRECV POWER *: *([-+]?[0-9]*\\.?[0-9]*)'
  if signal_power := findall(signal_power_pattern, show_optic_module):
    return signal_power[0]
  error_pattern = 'ERR *([+-]?[0-9]*)'
  if error := findall(error_pattern, show_optic_module):
    if error[0] == '-553':
      return 'off'
    elif error[0] == '-506':
      return 'not found'
    else:
      logger.error('get_signal_power({0}): error ({1})'.format(show_optic_module, error[0]))
      return 'error'
  logger.error('get_signal_power({0}): error'.format(show_optic_module))
  return 'error'


@supply_telnet_session
@Log(logger)
def get_onu_power_signal_by_id(onu_id, telnet=None):
  telnet.write(b'cd gpononu\n')
  telnet.read_until(b'Admin\\gpononu# ')

  telnet.write(
    'show optic_module slot {board_id} link {pon_id} onu {onu_number}\n'.format(
      board_id=get_board_id(onu_id=onu_id),
      pon_id=get_pon_id(onu_id=onu_id),
      onu_number=get_onu_number_from_id(onu_id=onu_id)
    ).encode('ascii')
  )

  return get_signal_power(show_optic_module=telnet.read_until(b'Admin\\gpononu# ', timeout=4).decode('ascii'))
