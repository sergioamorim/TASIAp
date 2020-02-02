#!/usr/bin/python3
# coding=iso-8859-1

import argparse
import logging
import snmp_configexample as snmp_config
import subprocess

logger = logging.getLogger('onu_set_cvlan')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/onu_set_cvlan.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def is_onu_id_valid(onu_id):
  return is_int(onu_id) and int(onu_id) > 1100 and int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9

def is_vlan_id_valid(vlan_id):
  return is_int(vlan_id) and int(vlan_id) > 0 and int(vlan_id) < 4096

def format_strhexoctet(strhexoctet):
  return strhexoctet.zfill(2).upper()

def hexstr_to_hexoctetstr(hexstr):
  if len(hexstr) > 2:
    return hexstr_to_hexoctetstr(hexstr[:-2])+' '+format_strhexoctet(hexstr[-2:])
  return format_strhexoctet(hexstr[-2:])

def int_to_hexoctetstr(intvalue):
  return hexstr_to_hexoctetstr(format(intvalue, 'x'))

def assure_two_octet_hexstr(hexstr):
  if len(hexstr) is 2:
    return '00 '+hexstr
  return hexstr

def set_cvlan(ip, community, onu_id, cvlan):
  logger.debug('set_cvlan: onu_id: {0} cvlan: {1}'.format(onu_id, cvlan))
  board_id = 12 if onu_id[:1] == '1' else 14
  pon_id = int(onu_id[1:2])
  onu_number = int(onu_id[2:])
  command = 'snmpset -v 2c -c {0} {1} 1.3.6.1.4.1.5875.91.1.8.1.1.1.5.1 x "42 47 4D 50 01 00 00 00 00 00 00 00 D7 AC FE 82 BB 34 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 {2} 00 {3} 00 {4} 00 01 00 7A 01 01 01 01 01 00 00 01 00 52 00 00 01 81 00 {5} 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 02 80 00 0F 42 40 00 0F 42 40 00 00 FF FF FF 81 00 FF FF FF 81 00 00 00 00 00 00 00"'.format(community, ip, int_to_hexoctetstr(board_id), int_to_hexoctetstr(pon_id), int_to_hexoctetstr(onu_number), assure_two_octet_hexstr(int_to_hexoctetstr(cvlan)))
  logger.debug('set_cvlan: command: {0}'.format(command))
  subprocess.run(command, shell=True)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU em que a VLAN vai ser configurada', default=None)
  parser.add_argument('-c', '--cvlan', dest='c', help='CVLAN a ser configurada na ONU', default=None)
  args = parser.parse_args()

  onu_id = None
  cvlan = None
  if args.i:
    if is_onu_id_valid(args.i):
      onu_id = str(args.i)
      if args.c:
        if is_vlan_id_valid(args.c):
          cvlan = int(args.c)
        elif args.c == 'cto':
          cvlan = 4000
        else:
          logger.error('CVLAN invalida.')
          return 1
      else:
        cvlan = int(onu_id[:2]+'00')
    else:
      logger.error('ID da ONU invalido.')
      return 1
  else:
    logger.error('Informe o ID da ONU.')
    return 1

  set_cvlan(snmp_config.ip, snmp_config.community, onu_id, cvlan)

  return 0

if __name__ == '__main__':
  main()