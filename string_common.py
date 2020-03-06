#!/usr/bin/env python3.8
# coding=utf-8

import re
import unicodedata

def is_onu_id_valid(onu_id):
  return is_int(onu_id) and int(onu_id) > 1100 and int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9

def is_vlan_id_valid(vlan_id):
  return is_int(vlan_id) and int(vlan_id) > 0 and int(vlan_id) < 4096

def is_serial_valid(serial):
  return re.search('([0-9A-Z]{4}[0-9A-Fa-f]{8})', serial) != None

def remove_accents(string):
  return str(unicodedata.normalize('NFD', string).encode('ascii', 'ignore').decode('utf-8'))

def sanitize_dumb(string):
  return string.replace(',',', ').replace('//','').replace(' /',', ').replace('\t','').replace(' ,',',').replace(' / ',', ').replace('  ',' ')

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def get_onu_id_from_repr(onu_repr):
  onu_repr_pattern = "([0-9])',board='<Board\(board_id='([0-9]{2})'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='([0-9]+)"
  regex_result = re.findall(onu_repr_pattern, onu_repr)
  board = regex_result[0][1]
  pon = regex_result[0][0]
  onu_number = regex_result[0][2]
  onu_id = '{0}{1}{2}{3}'.format('1' if board == '12' else '2', pon, '0' if int(onu_number) < 10 else '', onu_number)
  return onu_id

def sanitize_cto_vlan_name(cto_vlan_name):
  if len(cto_vlan_name) > 32:
    board_id = '1' if cto_vlan_name[7:9] == '12' else '2'
    onu_id = '{0}{1}{2}'.format(board_id, cto_vlan_name[13:14], cto_vlan_name[18:20])
    cto_actual_name = cto_vlan_name[31:].replace('-',' ')
    vlan = '({0}) '.format(cto_vlan_name[:5]) if cto_vlan_name[1:5] != onu_id else ''
    cto_sanitized_name = 'CTO {0} {1}{2}'.format(onu_id, vlan, cto_actual_name)
    return cto_sanitized_name
  return ''

def format_datetime(datetime_object):
  return datetime_object.strftime('%d/%m/%Y %H:%M:%S')

def format_onu_state(onu_state):
  return 'online' if onu_state == 'up' else 'offline'