#!/usr/bin/env python3.8
# coding=utf-8

import re
import argparse
from telnetlib import Telnet
from telnet_common import connect_su, str_to_telnet
from string_common import is_serial_valid
import telnet_config

def get_onu_id_from_serial(serial):
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    tn.write(str_to_telnet('cd gpononu'))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('show authorization slot all link all'))
    auth_table = tn.read_until(b'gpononu# ', timeout=1)
  if (serial_row := re.findall(',(.*)([0-9]{2})(.*)([0-9])(.*)([0-9]{1,2})(.*)A(.*)([up|dn])(.*)({0})(.*),', onu_repr))
    print(serial_row)
    for item in serial_row:
      print(repr(item))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--serial', dest='s', help='Serial da ONU a ser consultada.', default=None)
  args = parser.parse_args()

  if (serial := args.s):
    if is_serial_valid(serial):
      get_onu_id_from_serial(serial)
      return 0
    print('Serial inválido.')
    return 1

  print('Informe o serial da ONU.')
  return 1

if __name__ == '__main__':
  return main()