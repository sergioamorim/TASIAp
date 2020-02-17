#!/usr/bin/env python3.8
# coding=utf-8

import re
import argparse
from telnetlib import Telnet
from telnet_common import connect_su, str_to_telnet
from string_common import is_serial_valid
import telnet_config

def find_onu_by_serial(serial):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    tn.write(str_to_telnet('cd gpononu'))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('show authorization slot all link all'))
    auth_table = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8')
  serial_row_pattern = '([0-9]{0}) +([1-8]) +([0-9]+) +.* +A +(u?p?d?n?) +{1}'.format('{2}', serial)
  if (serial_row := re.findall(serial_row_pattern, auth_table)):
    board_id = '1' if serial_row[0][0] == '12' else '2'
    onu_number = '{0}{1}'.format('0' if int(serial_row[0][2]) < 10 else '', serial_row[0][2])
    return {'onuid': '{0}{1}{2}'.format(board_id, serial_row[0][1], onu_number), 'state': '{0}'.format(serial_row[0][3])}
  return None

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--serial', dest='s', help='Serial da ONU a ser consultada.', default=None)
  args = parser.parse_args()

  if (serial := args.s):
    if is_serial_valid(serial):
      print(find_onu_by_serial(serial))
      return 0
    print('Serial inválido.')
    return 1

  print('Informe o serial da ONU.')
  return 1

if __name__ == '__main__':
  main()