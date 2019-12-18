#!/usr/bin/python3
# coding=iso-8859-1

from telnetlib import Telnet
import argparse
import subprocess
import logging
import authorize_onu_config as config
import telnet_config

logger = logging.getLogger('authorize_onu')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/authorize_onu.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class OnuDevice:
  phy_id = None
  pon = None
  onu_type = None
  number = None
  def setNumber(self, number):
    self.number = number
  def autoset_cvlan(self):
    cvlan_list = ['','','','']
    if self.pon.board.board_id is 12:
      cvlan_list[0] = '1'
    elif self.pon.board.board_id is 14:
      cvlan_list[0] = '2'
    cvlan_list[1] = str(self.pon.pon_id)[-1:]
    #cvlan_list[2] = str(self.number)[-2:-1]
    cvlan_list[2] = '0'
    #cvlan_list[3] = str(self.number)[-1:]
    cvlan_list[3] = '0'
    self.cvlan = int(''.join(cvlan_list))
  def __init__(self, phy_id, pon, onu_type):
    self.phy_id = phy_id
    self.pon = pon
    self.onu_type = onu_type
    self.cvlan = None
  def __repr__(self):
    return "<OnuDevice(phy_id='{0}',pon='{1}',onu_type='{2}',number='{3}',cvlan='{4}')>".format(self.phy_id, repr(self.pon), self.onu_type, self.number, self.cvlan)

class Pon:
  pon_id = None
  board = None
  last_authorized_onu_number = None
  def setLastAuthorizedOnuNumber(self, last_authorized_onu_number):
    self.last_authorized_onu_number = last_authorized_onu_number
  def __init__(self, pon_id, board):
    self.pon_id = pon_id
    self.board = board
  def __repr__(self):
    return "<Pon(pon_id='{0}',board='{1}',last_authorized_onu_number='{2}')>".format(self.pon_id, repr(self.board), self.last_authorized_onu_number)

class Board:
  board_id = None
  def __init__(self, board_id):
    self.board_id = board_id
  def __repr__(self):
    return "<Board(board_id='{0}')>".format(self.board_id)



def format_strhexoctet(strhexoctet):
  return strhexoctet.zfill(2).upper()

def hexstr_to_hexoctetstr(hexstr):
  if len(hexstr) > 2:
    return hexstr_to_hexoctetstr(hexstr[:-2])+' '+format_strhexoctet(hexstr[-2:])
  return format_strhexoctet(hexstr[-2:])

def assure_two_octet_hexstr(hexstr):
  if len(hexstr) is 2:
    return '00 '+hexstr
  return hexstr

def int_to_hexoctetstr(intvalue):
  return hexstr_to_hexoctetstr(format(intvalue, 'x'))

def str_to_telnet(string):
  return string.encode('ascii')+b'\n'

def connect_gpononu(tn):
  tn.read_until(b'Login: ', timeout=10)
  tn.write(str_to_telnet(telnet_config.username))
  tn.read_until(b'Password: ', timeout=10)
  tn.write(str_to_telnet(telnet_config.password))
  tn.read_until(b'User> ', timeout=10)
  tn.write(str_to_telnet('enable'))
  tn.read_until(b'Password: ', timeout=10)
  tn.write(str_to_telnet(telnet_config.password_sudo))
  tn.read_until(b'Admin# ', timeout=10)
  tn.write(str_to_telnet('cd service'))
  tn.read_until(b'service# ', timeout=10)
  tn.write(str_to_telnet('terminal length 512'))
  tn.read_until(b'service# ', timeout=10)
  tn.write(str_to_telnet('cd gpononu'))
  tn.read_until(b'gpononu# ', timeout=10)

def disconnect_gpononu(tn):
  tn.write(str_to_telnet('cd ..'))
  tn.read_until(b'Admin# ', timeout=10)
  tn.write(str_to_telnet('quit'))
  tn.close()

def get_next_value(tn):
  value = tn.read_until(b' ', timeout=10)
  while ' '.encode('ascii') in value[:-1] or ' '.encode('ascii') is value or '\n'.encode('ascii') in value[:-1]:
    value = tn.read_until(b' ', timeout=10)
  return value[:-1].decode('utf-8')

def authorize_onu(onu):
  onu.setNumber(onu.pon.last_authorized_onu_number+1)
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('set whitelist phy_addr address '+onu.phy_id+' password null action delete'))
    tn.read_until(b'gpononu#', timeout=10)
    tn.write(str_to_telnet('set authorization slot '+str(onu.pon.board.board_id)+' link '+str(onu.pon.pon_id)+' type '+onu.onu_type+' onuid '+str(onu.number)+' phy_id '+onu.phy_id))
    tn.read_until(b'gpononu#', timeout=10)
    tn.write(str_to_telnet('set whitelist phy_addr address '+onu.phy_id+' password null action add slot '+str(onu.pon.board.board_id)+' link '+str(onu.pon.pon_id)+' onu '+str(onu.number)+' type '+onu.onu_type))
    disconnect_gpononu(tn)

def set_cvlan(ip, community, onu, predefined_cvlan):
  if predefined_cvlan:
    onu.cvlan = predefined_cvlan
  else:
    onu.autoset_cvlan()
  logger.debug('set_cvlan: onu.cvlan: {0}'.format(onu.cvlan))
  command = 'snmpset -v 2c -c ' + community + ' ' + ip + ' 1.3.6.1.4.1.5875.91.1.8.1.1.1.5.1 x "42 47 4D 50 01 00 00 00 00 00 00 00 D7 AC FE 82 BB 34 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 A3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' + int_to_hexoctetstr(onu.pon.board.board_id) + ' 00 ' + int_to_hexoctetstr(onu.pon.pon_id) + ' 00 ' + int_to_hexoctetstr(onu.number) + ' 00 01 00 7A 01 01 01 01 01 00 00 01 00 52 00 00 01 81 00 ' + assure_two_octet_hexstr(int_to_hexoctetstr(onu.cvlan)) + ' 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 81 00 FF FF FF 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 02 80 00 0F 42 40 00 0F 42 40 00 00 FF FF FF 81 00 FF FF FF 81 00 00 00 00 00 00 00"'
  subprocess.run(command, shell=True)

def get_new_onu_number(tn, onu_quantity, pon):
  last_authorized_onu_number = 0
  for i in range(0,onu_quantity):
    tn.read_until(str(pon.board.board_id).encode('ascii'), timeout=10)
    tn.read_until(str(pon.pon_id).encode('ascii'), timeout=10)
    current_onu_number = int(get_next_value(tn))
    if current_onu_number == last_authorized_onu_number + 1:
      last_authorized_onu_number = current_onu_number
    else:
      return last_authorized_onu_number
    tn.read_until(b',', timeout=10)
  return last_authorized_onu_number

def is_int(s):
  try: 
    int(s)
    return True
  except ValueError:
    return False

parser = argparse.ArgumentParser()

parser.add_argument("-a", "--authorize-onu", dest="a", help="Numero da ONU que deve ser autorizada da lista de ONUs disponiveis para autorizacao", default=None)
parser.add_argument("-v", "--cvlan", dest="v", help="CVLAN para configurar a ONU", default=None)

args = parser.parse_args()

auth_onu = str(args.a) if args.a else None
predefined_cvlan = int(args.v) if args.v else None

onu_list = []
pon_list = []
board_list = []

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
      board_list.append(board)
      pon = Pon(pon_id,board)
      pon_list.append(pon)
      tn.read_until(b'  --------------------------', timeout=10)
      for i in range(0,unauthorized_onu_quantity):
        onu_type = get_next_value(tn).lower()
        if 'an' in onu_type[:2]:
          onu_type = onu_type[2:]
        phy_id = get_next_value(tn)
        onu_list.append(OnuDevice(phy_id,pon,onu_type))
        tn.read_until(b',', timeout=10)
    if '----- '.encode('ascii') in tn.read_until(b'----- ', timeout=1):
      end_of_pon_list = False
    else:
      end_of_pon_list = True
  disconnect_gpononu(tn)

for pon in pon_list:
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_gpononu(tn)
    tn.write(str_to_telnet('show authorization slot '+str(pon.board.board_id)+' link '+str(pon.pon_id)))
    tn.read_until(b'ITEM=', timeout=10)
    onu_quantity = int(get_next_value(tn))
    tn.read_until(b' --------------------', timeout=10)
    last_authorized_onu_number = get_new_onu_number(tn, onu_quantity, pon)
    pon.setLastAuthorizedOnuNumber(last_authorized_onu_number)
    tn.read_until(b'gpononu# ', timeout=10)
    disconnect_gpononu(tn)

if not len(onu_list):
  print('None')
else:
  if not auth_onu:
    for i, onu in enumerate(onu_list):
      print('{0}_{1}_{2}'.format(onu.pon.board.board_id, onu.pon.pon_id, onu.phy_id), end=' ')
    print('')
  elif is_int(auth_onu):
    authed = False
    for i, onu in enumerate(onu_list):
      logger.debug('loop to authorize onu: auth_onu: {0} current position in list: {1}'.format(auth_onu, str(i+1)))
      if auth_onu == str(i+1):
        authorize_onu(onu)
        set_cvlan(telnet_config.ip, config.snmp_community, onu, predefined_cvlan)
        authed = True
        print(repr(onu))
    if not authed:
      print('ERR')