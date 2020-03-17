from argparse import ArgumentParser
from telnetlib import Telnet

from common.telnet_common import str_to_telnet, get_next_value, connect_su
from config import telnet_config
from logger import get_logger

logger = get_logger(__name__)


def get_onu_power_signal_by_id(tn, onu_id):
  logger.debug('get_onu_power_signal_by_id({0}, {1})'.format(repr(tn), repr(onu_id)))
  board = '12' if onu_id[:1] == '1' else '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'gpononu# ', timeout=1)
  tn.write(str_to_telnet('show optic_module slot {0} link {1} onu {2}'.format(board, pon, onu_number)))
  tn.read_until(b'\n', timeout=3)
  value = get_next_value(tn, ' ')
  if value != '-----':
    value = get_next_value(tn, ']')
    if '-553' in value:
      signal_power = 'off'
    elif '-506' in value:
      signal_power = 'not found'
    else:
      signal_power = 'error'
  else:
    tn.read_until(b'RECV POWER   :', timeout=3)
    signal_power = get_next_value(tn, '\t')[1:]
  tn.read_until(b'gpononu# ', timeout=1)
  logger.debug('get_onu_power_signal_by_id({0}, {1}): {2}'.format(repr(tn), repr(onu_id), repr(signal_power)))
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
