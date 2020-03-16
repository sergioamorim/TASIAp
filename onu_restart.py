from argparse import ArgumentParser
from telnetlib import Telnet

from common.string_common import is_onu_id_valid
from common.telnet_common import connect_su, str_to_telnet
from config import telnet_config
from logger import get_logger

logger = get_logger(__name__)


def restart_onu(board, pon, onu_number):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    tn.write(str_to_telnet('cd gpononu'))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('reset slot {0} link {1} onulist {2}'.format(board, pon, onu_number)))
    result = tn.read_until(b'gpononu# ', timeout=3).decode('ascii')
  if 'no onu satisfy the list' in result:
    restart_result = 'not found'
  elif 'reset onu ok' in result:
    restart_result = 'done'
  else:
    restart_result = 'error'
  return restart_result


def restart_onu_by_id(onu_id):
  logger.debug('restart_onu_by_id({0})'.format(repr(onu_id)))
  if not onu_id or not is_onu_id_valid(onu_id):
    logger.debug('restart_onu_by_id({0}): can not restart onu'.format(repr(onu_id)))
    return None
  board = '12' if onu_id[:1] == '1' else '14'
  pon = onu_id[1:2]
  onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
  result = restart_onu(board, pon, onu_number)
  logger.debug('restart_onu_by_id({0}): {1}'.format(repr(onu_id), repr(result)))
  return result


def main():
  parser = ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser reiniciada', default=None)
  args = parser.parse_args()

  print(restart_onu_by_id(args.i))

  return 0


if __name__ == '__main__':
  main()
