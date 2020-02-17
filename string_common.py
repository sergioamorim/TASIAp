#!/usr/bin/env python3.8
# coding=utf-8

import re

def is_onu_id_valid(onu_id):
  return is_int(onu_id) and int(onu_id) > 1100 and int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9

def is_vlan_id_valid(vlan_id):
  return is_int(vlan_id) and int(vlan_id) > 0 and int(vlan_id) < 4096

def is_serial_valid(serial):
  return re.search('([0-9A-Z]{4}[0-9A-Fa-f]{8})', serial) != None

def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def get_onu_info_string(onu_repr=None, onu_id=None, cvlan=None, serial=None):
  signal = None
  if onu_repr:
    onu_repr_pattern = "([0-9A-Z]{4}[0-9A-Fa-f]{8})',pon='<Pon\(pon_id='[0-9]',board='<Board\(board_id='[0-9]{2}'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='[0-9]+',cvlan='(N?o?n?e?[0-9]{0,4})"
    regex_result = re.findall(onu_repr_pattern, onu_repr)
    serial = regex_result[0][0]
    if (cvlan := regex_result[0][1]) != 'None':
      cvlan = cvlan[0]
    onu_id = get_onu_id_from_repr(onu_repr)
  else:
    signal = get_signal(onu_id)
  return 'ID: {0}{1}\nSerial: {2}{3}'.format(onu_id, '\nCVLAN: {0}'.format(cvlan) if cvlan else '', serial, '\nSinal: {0}'.format(signal) if signal else '')

def get_onu_id_from_repr(onu_repr):
  onu_repr_pattern = "([0-9])',board='<Board\(board_id='([0-9]{2})'\)>',last_authorized_onu_number='[0-9]+'\)>',onu_type='.*',number='([0-9]+)"
  regex_result = re.findall(onu_repr_pattern, onu_repr)
  board = regex_result[0][1]
  pon = regex_result[0][0]
  onu_number = regex_result[0][2]
  onu_id = '{0}{1}{2}{3}'.format('1' if board == '12' else '2', pon, '0' if int(onu_number) < 10 else '', onu_number)
  return onu_id

def sanitize_cto_vlan_name(cto_vlan_name):
  vlan = cto_vlan_name[:5]
  if cto_vlan_name[7:9] == '12':
    board_id = '1'
  else:
    board_id = '2'
  pon = cto_vlan_name[13:14]
  onu_number = cto_vlan_name[18:20]
  onu_id = '{0}{1}{2}'.format(board_id, pon, onu_number)
  cto_actual_name = cto_vlan_name[31:].replace('-',' ')
  cto_sanitized_name = 'CTO {0}{1}{2}'.format(onu_id, ' ({0}) '.format(vlan) if vlan[1:] != onu_id else ' ', cto_actual_name)
  return cto_sanitized_name