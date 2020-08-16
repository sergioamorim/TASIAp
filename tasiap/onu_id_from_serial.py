from re import findall

from tasiap.common.telnet_common import str_to_telnet, supply_telnet_session
from tasiap.logger import Log, get_logger

logger = get_logger(__name__)


@supply_telnet_session
@Log(logger)
def find_onu_by_serial(serial, telnet=None):
  telnet.write(str_to_telnet('cd gpononu'))
  telnet.read_until(b'gpononu# ', timeout=1)
  telnet.write(str_to_telnet('show authorization slot all link all'))
  auth_table = telnet.read_until(b'gpononu# ', timeout=1).decode('utf-8')
  serial_row_pattern = '([0-9]{0}) +([1-8]) +([0-9]+) +.* +A +(u?p?d?n?) +{1}'.format('{2}', serial)
  if serial_row := findall(serial_row_pattern, auth_table):
    board_id = '1' if serial_row[0][0] == '12' else '2'
    onu_number = '{0}{1}'.format('0' if int(serial_row[0][2]) < 10 else '', serial_row[0][2])
    onu_info = {'onu_id': '{0}{1}{2}'.format(board_id, serial_row[0][1], onu_number),
                'state': '{0}'.format(serial_row[0][3])}
    return onu_info
  return None
