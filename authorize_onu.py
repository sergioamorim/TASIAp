#!/usr/bin/python3
# coding=iso-8859-1

from telnetlib import Telnet
import argparse
import subprocess
import telnet_config
import re

from logger import logger
from string_common import is_int, is_vlan_id_valid
from telnet_common import str_to_telnet, connect_su


class OnuDevice:
  phy_id = None
  pon = None
  onu_type = None
  number = None
  cvlan = None

  def __init__(self, phy_id, pon, onu_type):
    self.phy_id = phy_id
    self.pon = pon
    self.onu_type = onu_type

  def __repr__(self):
    return "<OnuDevice(phy_id='{0}',pon='{1}',onu_type='{2}',number='{3}',cvlan='{4}')>".format(self.phy_id,
                                                                                                repr(self.pon),
                                                                                                self.onu_type,
                                                                                                self.number, self.cvlan)


class Pon:
  pon_id = None
  board = None
  last_authorized_onu_number = None

  def __init__(self, pon_id, board):
    self.pon_id = pon_id
    self.board = board

  def __repr__(self):
    return "<Pon(pon_id='{0}',board='{1}',last_authorized_onu_number='{2}')>".format(self.pon_id, repr(self.board),
                                                                                     self.last_authorized_onu_number)


class Board:
  board_id = None

  def __init__(self, board_id):
    self.board_id = board_id

  def __repr__(self):
    return "<Board(board_id='{0}')>".format(self.board_id)


def get_next_value(tn):
  value = tn.read_until(b' ', timeout=10)
  while ' '.encode('ascii') in value[:-1] or ' '.encode('ascii') is value or '\n'.encode('ascii') in value[:-1]:
    value = tn.read_until(b' ', timeout=10)
  return value[:-1].decode('utf-8')


def connect_gpononu(tn):
  connect_su(tn)
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'gpononu# ', timeout=10)


def authorize_onu(onu, cvlan):
  onu.number = onu.pon.last_authorized_onu_number + 1
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('set whitelist phy_addr address ' + onu.phy_id + ' password null action delete'))
    tn.read_until(b'gpononu#', timeout=10)
    tn.write(str_to_telnet('set authorization slot ' + str(onu.pon.board.board_id) + ' link ' + str(
      onu.pon.pon_id) + ' type ' + onu.onu_type + ' onuid ' + str(onu.number) + ' phy_id ' + onu.phy_id))
    tn.read_until(b'gpononu#', timeout=10)
    tn.write(str_to_telnet('set whitelist phy_addr address ' + onu.phy_id + ' password null action add slot ' + str(
      onu.pon.board.board_id) + ' link ' + str(onu.pon.pon_id) + ' onu ' + str(onu.number) + ' type ' + onu.onu_type))
  if cvlan:
    set_cvlan(onu, cvlan)
  return onu


def set_cvlan(onu, cvlan):
  onu_id = '{0}{1}{2}'.format('1' if onu.pon.board.board_id == 12 else '2', onu.pon.pon_id, onu.number)
  command_list = ['python3', 'onu_set_cvlan.py', '-i', '{0}'.format(onu_id), '-c', '{0}'.format(cvlan)]
  answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8')
  cvlan_commited = re.findall('_([0-9]{4})', answer_string)[0]
  onu.cvlan = int(cvlan_commited)


def get_new_onu_number(tn, onu_quantity, pon):
  last_authorized_onu_number = 0
  for i in range(0, onu_quantity):
    tn.read_until(str(pon.board.board_id).encode('ascii'), timeout=10)
    tn.read_until(str(pon.pon_id).encode('ascii'), timeout=10)
    current_onu_number = int(get_next_value(tn))
    if current_onu_number == last_authorized_onu_number + 1:
      last_authorized_onu_number = current_onu_number
    else:
      return last_authorized_onu_number
    tn.read_until(b',', timeout=10)
  return last_authorized_onu_number


def find_onu_in_list(onu_list, auth_onu):
  if is_int(auth_onu):
    for i, onu in enumerate(onu_list):
      if auth_onu == str(i + 1):
        return onu
  else:
    for onu in onu_list:
      if onu.phy_id == auth_onu:
        return onu
  return None


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-a", "--authorize-onu", dest="a",
                      help="Numero da ONU que deve ser autorizada da lista de ONUs disponiveis para autorizacao",
                      default=None)
  parser.add_argument("-c", "--cvlan", dest="c", help="CVLAN para configurar a ONU", default=None)
  args = parser.parse_args()

  auth_onu = str(args.a).replace(' ', '') if args.a else None
  cvlan = None
  if args.c:
    if is_vlan_id_valid(args.c) or args.c == 'cto':
      cvlan = str(args.c)
    else:
      logger.error('CVLAN invalida.')
      return 1

  onu_list = []
  pon_list = []
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('show discovery slot all link all'))
    end_of_pon_list = False
    while not end_of_pon_list:
      tn.read_until(b' ONU Unauth Table ,SLOT=', timeout=10)
      board_id = int(get_next_value(tn))
      tn.read_until(b'PON=', timeout=10)
      pon_id = int(get_next_value(tn))
      tn.read_until(b',ITEM=', timeout=10)
      unauthorized_onu_quantity = int(tn.read_until(b'-', timeout=10)[:-1])
      tn.read_until(b'----', timeout=10)
      if unauthorized_onu_quantity:
        board = Board(board_id)
        pon = Pon(pon_id, board)
        pon_list.append(pon)
        tn.read_until(b'  --------------------------', timeout=10)
        for i in range(0, unauthorized_onu_quantity):
          onu_type = get_next_value(tn).lower()
          if 'an' in onu_type[:2]:
            onu_type = onu_type[2:]
          phy_id = get_next_value(tn)
          onu_list.append(OnuDevice(phy_id, pon, onu_type))
          tn.read_until(b',', timeout=10)
      if '----- '.encode('ascii') in tn.read_until(b'----- ', timeout=1):
        end_of_pon_list = False
      else:
        end_of_pon_list = True

  for pon in pon_list:
    with Telnet(telnet_config.ip, telnet_config.port) as tn:
      connect_gpononu(tn)
      tn.write(str_to_telnet('show authorization slot ' + str(pon.board.board_id) + ' link ' + str(pon.pon_id)))
      tn.read_until(b'ITEM=', timeout=10)
      onu_quantity = int(get_next_value(tn))
      tn.read_until(b' --------------------', timeout=10)
      last_authorized_onu_number = get_new_onu_number(tn, onu_quantity, pon)
      pon.last_authorized_onu_number = last_authorized_onu_number
      tn.read_until(b'gpononu# ', timeout=10)

  if not len(onu_list):
    print('None')
  else:
    if not auth_onu:
      for i, onu in enumerate(onu_list):
        print('{0}_{1}_{2}'.format(onu.pon.board.board_id, onu.pon.pon_id, onu.phy_id), end=' ')
      print('')
    else:
      onu = find_onu_in_list(onu_list, auth_onu)
      if onu:
        print(repr(authorize_onu(onu, cvlan)))
      else:
        print('ERR')


if __name__ == '__main__':
  main()
