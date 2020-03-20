from argparse import ArgumentParser
from re import findall
from telnetlib import Telnet

from common.telnet_common import str_to_telnet, connect_su
from config import telnet_config
from logger import Log, get_logger

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


@Log(logger)
def get_onu_power_signal_by_id(tn, onu_id):
  board = '12' if onu_id[:1] == '1' else '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'Admin\\gpononu# ', timeout=1)
  tn.write(str_to_telnet('show optic_module slot {0} link {1} onu {2}'.format(board, pon, onu_number)))
  show_optic_module = tn.read_until(b'Admin\\gpononu# ', timeout=3).decode('ascii')
  signal_power = get_signal_power(show_optic_module)
  return signal_power


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser consultada', default=None)
  args = parser.parse_args()

  onu_id = None
  if args.i:
    onu_id = str(args.i)

  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    signal_power = get_onu_power_signal_by_id(tn, onu_id)
    print(signal_power)


if __name__ == '__main__':
  main()
