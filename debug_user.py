#!/usr/bin/python3.6
# coding=utf-8

import argparse
import logging
import re
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telnetlib import Telnet
import debug_user_config as config
import telnet_config

logger = logging.getLogger('debug_user')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('debug_user.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def str_to_telnet(string):
  return string.encode('ascii')+b'\n'

class Login:
  username = None
  password = None
  plan = None
  ip = None
  mac = None
  onu = None
  enable = None
  client_id = None
  def autoset_info(self, session):
    info_query = session.execute("SELECT pass, groupname, ip, mac, enable, cliente_id FROM {0} WHERE user = :username;".format(config.mysql['login_table']), {'username': self.username}).first()
    self.password = info_query[0]
    self.plan = info_query[1]
    self.ip = info_query[2]
    self.mac = info_query[3]
    self.enable = True if info_query[4] == 1 else False
    self.client_id = info_query[5]
  def __repr__(self):
    return "<Login(username='{0}',password='{1}',plan='{2}',ip='{3}',mac='{4}',onu='{5}',enable='{6}',client_id='{7}')>".format(self.username, self.password, self.plan, self.ip, self.mac, self.onu, self.enable, self.client_id)
  def __str__(self):
    return 'username: {0} password: {1} plan: {2} ip: {3} mac: {4} onu: {5} enable: {6} client_id= {7}'.format(self.username, self.password, self.plan, self.ip, self.mac, self.onu, self.enable, self.client_id)
  def __init__(self, session, onu, username):
    self.username = username
    self.onu = onu
    self.autoset_info(session)

class Onu:
  phy_address = None
  board = None
  pon = None
  onu_number = None
  signal_power = None
  vlan = None
  associated_mac_list = []
  def autoset_vlan_and_macs(self, tn):
    tn.write(str_to_telnet('cd gponline'))
    tn.read_until(b'gponline# ', timeout=1)
    tn.write(str_to_telnet('show pon_mac slot {0} link {1}'.format(self.board, self.pon)))
    remove_header_value = tn.read_until(b'-----\n\r001\t', timeout=1)
    logger.debug('Onu: autoset_vlan_and_macs: remove_header: {0}'.format(remove_header_value))
    if 'gponline#' in remove_header_value.decode('utf-8'):
      logger.error('Onu: autoset_vlan_and_macs: onu not found!')
      return
    found = False
    logger.debug('Onu: autoset_vlan_and_macs: starting find onu_number: {0}'.format(self.onu_number))
    while not found:
      value = get_next_value(tn, '\t')
      if '--Press' in value:
        logger.debug('Onu: autoset_vlan_and_macs: while not found: catch --Press: value: {0}'.format(value))
        tn.write(str_to_telnet('\n'))
        tn.read_until(b'Master', timeout=1)
        value = get_next_value(tn, '\t')
      current_mac = value
      logger.debug('Onu: autoset_vlan_and_macs: while not found: current_mac: {0}'.format(current_mac))
      current_vlan = get_next_value(tn, ' ')[4:]
      logger.debug('Onu: autoset_vlan_and_macs: while not found: current_vlan: {0}'.format(current_vlan))
      current_onu_number = get_next_value(tn, '\n')[6:]
      logger.debug('Onu: autoset_vlan_and_macs: while not found: current_onu_number: {0}'.format(current_onu_number))
      waste_value = get_next_value(tn, '\t')
      logger.debug('Onu: autoset_vlan_and_macs: while not found: waste value: {0}'.format(waste_value.replace('\r','')))
      if 'gponline#' in waste_value:
        logger.error('Onu: autoset_vlan_and_macs: onu not found!')
        return
      if current_onu_number == self.onu_number:
        logger.debug('Onu: autoset_vlan_and_macs: catch right onu_number')
        self.associated_mac_list.append(current_mac)
        self.vlan = current_vlan
        found = True
    same_onu = True
    while same_onu:
      value = get_next_value(tn, '\t')
      if value == '--Press':
        logger.debug('Onu: autoset_vlan_and_macs: while same_onu: catch --Press')
        tn.write(str_to_telnet('\n'))
        tn.read_until(b'Master', timeout=1)
        value = get_next_value(tn, '\t')
      current_mac = value
      logger.debug('Onu: autoset_vlan_and_macs: while same_onu: current_mac: {0}'.format(current_mac))
      current_vlan = get_next_value(tn, ' ')[4:]
      logger.debug('Onu: autoset_vlan_and_macs: while same_onu: current_vlan: {0}'.format(current_vlan))
      if current_vlan == self.vlan:
        logger.debug('Onu: autoset_vlan_and_macs: while same_onu: same vlan')
        current_onu_number = get_next_value(tn, '\n')[6:]
        logger.debug('Onu: autoset_vlan_and_macs: while same_onu: current_onu_number: {0}'.format(current_onu_number))
        if current_onu_number == self.onu_number:
          logger.debug('Onu: autoset_vlan_and_macs: while same_onu: same vlan: same onu_number')
          self.associated_mac_list.append(current_mac)
          waste_value = get_next_value(tn, '\t')
          logger.debug('Onu: autoset_vlan_and_macs: while not found: waste value: {0}'.format(waste_value))
        else:
          logger.debug('Onu: autoset_vlan_and_macs: while same_onu: same vlan: different onu_number'.format)
          same_onu = False
      else:
        logger.debug('Onu: autoset_vlan_and_macs: while same_onu: different vlan')
        same_onu = False
    waste_value = tn.read_until(b'gponline# ', timeout=1).decode('utf-8')
    logger.debug('Onu: autoset_vlan_and_macs: finalizing: catch gponline#: waste_value: {0}'.format(waste_value))
    while 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      logger.debug('Onu: autoset_vlan_and_macs: finalizing: catch stop--: waste_value: {0}'.format(waste_value))
      waste_value = tn.read_until(b'gponline# ', timeout=1).decode('utf-8')
      logger.debug('Onu: autoset_vlan_and_macs: finalizing: catch gponline#: waste_value: {0}'.format(waste_value))
    tn.write(str_to_telnet('cd ..'))
    tn.read_until(b'Admin# ', timeout=1)
    logger.debug('Onu: autoset_vlan_and_macs: stoped...')
  def autoset_signal_power(self, tn):
    tn.write(str_to_telnet('cd gpononu'))
    waste_value = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8').replace('\r','')
    logger.debug('Onu: autoset_signal_power: waste_value 1: {0}'.format(waste_value))
    if 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      waste_value = tn.read_until(b'gpononu# ', timeout=1).decode('utf-8').replace('\r','')
      logger.debug('Onu: autoset_signal_power: waste_value 2: {0}'.format(waste_value))
    tn.write(str_to_telnet('show optic_module slot {0} link {1} onu {2}'.format(self.board, self.pon, self.onu_number)))
    logger.debug('Onu: autoset_signal_power: tn.write: {0}'.format(repr('show optic_module slot {0} link {1} onu {2}'.format(self.board, self.pon, self.onu_number))))
    waste_value = tn.read_until(b'\n', timeout=3).decode('utf-8').replace('\r','')
    logger.debug('Onu: autoset_signal_power: waste_value 3: {0}'.format(waste_value))
    if 'stop--' in waste_value:
      tn.write(str_to_telnet('\n'))
      waste_value = tn.read_until(b'\n', timeout=3).decode('utf-8').replace('\r','')
      logger.debug('Onu: autoset_signal_power: waste_value 4: {0}'.format(waste_value))
    value = get_next_value(tn, ' ')
    logger.debug('Onu: autoset_signal_power: try to catch -553: {0}'.format(value))
    if value != '-----':
      self.signal_power = 'off'
    else:
      waste_value = tn.read_until(b'RECV POWER   :', timeout=3).decode('utf-8').replace('\r','')
      logger.debug('Onu: autoset_signal_power: waste_value 5: {0}'.format(waste_value))
      if 'stop--' in waste_value:
        tn.write(str_to_telnet('\n'))
        waste_value = tn.read_until(b'RECV POWER   :', timeout=3).decode('utf-8').replace('\r','')
        logger.debug('Onu: autoset_signal_power: waste_value 6: {0}'.format(waste_value))
      self.signal_power = get_next_value(tn, '\t')[1:]
    logger.debug('Onu: autoset_signal_power: self.signal_power: {0}'.format(self.signal_power))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('cd ..'))
    tn.read_until(b'Admin# ', timeout=1)
  def autoset_info_by_mac(self, tn, mac):
    pon_list = get_pon_list(tn)
    tn.write(str_to_telnet('cd gponline'))
    tn.read_until(b'gponline# ', timeout=1)
    logger.debug('Onu: autoset_info_by_mac: starting find mac: {0}'.format(mac))
    found = False
    for pon in pon_list:
      if not found:
        tn.write(str_to_telnet('show pon_mac {0}'.format(pon)))
        remove_header_value = tn.read_until(b'-----\n\r001\t', timeout=1)
        logger.debug('Onu: autoset_info_by_mac: remove_header: {0}'.format(remove_header_value))
        end_of_list = False
        if 'gponline#' in remove_header_value.decode('utf-8'):
          end_of_list = True
        while not found and not end_of_list:
          value = get_next_value(tn, '\t')
          if '--Press' in value:
            logger.debug('Onu: autoset_info_by_mac: while not found: catch --Press: value: {0}'.format(value))
            tn.write(str_to_telnet('\n'))
            tn.read_until(b'Master', timeout=1)
            value = get_next_value(tn, '\t')
          current_mac = value
          logger.debug('Onu: autoset_info_by_mac: while not found: current_mac: {0}'.format(current_mac))
          current_vlan = get_next_value(tn, ' ')[4:]
          logger.debug('Onu: autoset_info_by_mac: while not found: current_vlan: {0}'.format(current_vlan))
          current_onu_number = get_next_value(tn, '\n')[6:]
          logger.debug('Onu: autoset_info_by_mac: while not found: current_onu_number: {0}'.format(current_onu_number))
          if current_mac == mac:
            logger.debug('Onu: autoset_info_by_mac: catch right mac: {0} == {1}'.format(current_mac, mac))
            self.associated_mac_list.append(current_mac)
            self.vlan = current_vlan
            logger.debug('Onu: autoset_info_by_mac: catch right mac: vlan: {0}'.format(self.vlan))
            self.onu_number = current_onu_number
            logger.debug('Onu: autoset_info_by_mac: catch right mac: onu_number: {0}'.format(self.onu_number))
            self.pon = pon[13:15].replace(' ','')            
            logger.debug('Onu: autoset_info_by_mac: catch right mac: pon: {0}'.format(self.pon))
            self.board = pon[5:7]
            logger.debug('Onu: autoset_info_by_mac: catch right mac: board: {0}'.format(self.board))
            found = True
          waste_value = get_next_value(tn, '\t')
          logger.debug('Onu: autoset_info_by_mac: while not found: waste_value: {0}'.format(waste_value.replace('\r','')))
          if 'gponline#' in waste_value:
            end_of_list = True
          elif 'stop--' in waste_value:
            logger.debug('Onu: autoset_vlan_and_macs: while same_onu: catch --Press')
            tn.write(str_to_telnet('\n'))
            tn.read_until(b'Master', timeout=1)
            waste_value = get_next_value(tn, '\t')
    tn.write(str_to_telnet('cd ..'))
    waste_value = tn.read_until(b'Admin# ', timeout=1).decode('utf-8')
    logger.debug('Onu: autoset_info_by_mac: finalizing: catch Admin#: {0}'.format(waste_value.replace('\r','')))
  def autoset_phy_address(self, tn):
    tn.write(str_to_telnet('cd gpononu'))
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('show authorization slot {0} link {1}'.format(self.board, self.pon)))
    tn.read_until(b'ITEM=', timeout=1)
    onu_sum = get_next_value(tn, ' ')
    logger.debug('Onu: autoset_phy_address: onu_sum: {0}'.format(onu_sum))
    for i in range(0,2): tn.read_until(b'\r', timeout=1)
    found = False
    for i in range(0,int(onu_sum)):
      if not found:
        waste_value = tn.read_until(b'\r', timeout=1).decode('utf-8')
        logger.debug('Onu: autoset_phy_address: while not found waste_value: {0}'.format(waste_value.replace('\r','')))
        current_slot = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_slot: {0}'.format(current_slot))
        if '\n' in current_slot:
          logger.debug('Onu: autoset_phy_address: current_slot: \\n: catch --Press'.format(current_slot))
          tn.write(str_to_telnet('\n'))
          tn.read_until(b'Master', timeout=1)
          tn.read_until(b'\r', timeout=1)
          current_slot = get_next_value(tn, ' ')
          logger.debug('Onu: autoset_phy_address: new current_slot: {0}'.format(current_slot))
        current_pon = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_pon: {0}'.format(current_pon))
        current_onu_number = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_onu_number: {0}'.format(current_onu_number))
        current_onu_type_model = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_onu_type_model: {0}'.format(current_onu_type_model))
        current_onu_auth_state = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_onu_auth_state: {0}'.format(current_onu_auth_state))
        current_onu_online_state = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_onu_online_state: {0}'.format(current_onu_online_state))
        current_onu_phy_address = get_next_value(tn, ' ')
        logger.debug('Onu: autoset_phy_address: current_onu_phy_address: {0}'.format(current_onu_phy_address))
        if current_onu_number == self.onu_number:
          self.phy_address = current_onu_phy_address
          found = True
    tn.read_until(b'gpononu# ', timeout=1)
    tn.write(str_to_telnet('cd ..'))
    tn.read_until(b'Admin# ', timeout=1)
  def __repr__(self):
    return "<Onu(phy_address='{0}',board='{1}',pon='{2}',onu_number='{3}',signal_power='{4}',vlan='{5}',associated_mac_list='{6}')>".format(self.phy_address, self.board, self.pon, self.onu_number, self.signal_power, self.vlan, repr(self.associated_mac_list))
  def __str__(self):
    return 'phy_address: {0} board: {1} pon: {2} onu_number: {3} signal_power: {4} vlan: {5} associated_mac_list: {6}'.format(self.phy_address, self.board, self.pon, self.onu_number, self.signal_power, self.vlan, self.associated_mac_list)
  def __init__(self, tn, string=None, mac=None, onu_id=None):
    if string:
      self.phy_address = re.findall(".*phy_id\\=\\'([0-9A-Z]{4}[0-9A-Fa-f]{8}).*", string)[0]
      self.board = re.findall(".*board_id\\=\\'([0-9]{2}).*", string)[0]
      self.pon = re.findall(".*pon_id\\=\\'([0-9]).*", string)[0]
      self.onu_number = re.findall(".*number\\=\\'([0-9]*)'.*", string)[0]
      self.autoset_vlan_and_macs(tn)
      self.autoset_signal_power(tn)
    elif mac:
      self.autoset_info_by_mac(tn, mac)
      self.autoset_phy_address(tn)
      self.autoset_signal_power(tn)
    elif onu_id:
      if onu_id[:1] == '1':
        self.board = '12'
      elif onu_id[:1] == '2':
        self.board = '14'
      self.pon = onu_id[1:2]
      self.onu_number = onu_id[2:] if int(onu_id[2:]) > 9 else onu_id[3:]
      self.autoset_vlan_and_macs(tn)
      self.autoset_phy_address(tn)
      self.autoset_signal_power(tn)

class Client:
  client_id = None
  cpf = None
  name = None
  address = None
  enable = None
  logins = []
  def autoset_info(self, session):
    info_query = session.execute("SELECT cpfcnpj, nome, endereco, numero, complemento, referencia, bairro, status FROM {0} WHERE id = :client_id;".format(config.mysql['clientes_table']), {'client_id': self.client_id}).first()
    self.cpf = info_query[0]
    self.name = sanitize_name(info_query[1])
    self.address = '{0}, {1}\n{2} {3}\n{4}'.format(info_query[2], info_query[3], sanitize_dumb(info_query[4]), sanitize_dumb(info_query[5]), info_query[6])
    self.enable = True if info_query[7] == 1 else False
  def __repr__(self):
    return "<Client(cpf='{0}',name='{1}',address='{2}',enable='{3}',logins='{4}')>".format(self.cpf, self.name, self.address, repr(self.logins))
  def __str__(self):
    return 'cpf: {0} name: {1} address: {2} enable: {3} logins: {4}'.format(self.cpf, self.name, self.address, self.logins)
  def __init__(self, session, client_id):
    self.client_id = client_id
    self.autoset_info(session)

def get_pon_list(tn):
  tn.write(str_to_telnet('cd gponline'))
  tn.read_until(b'gponline# ', timeout=1)
  tn.write(str_to_telnet('show pon_auth all'))
  tn.read_until(b'ITEM=', timeout=1)
  pon_sum = get_next_value(tn, ' ')
  logger.debug('get_pon_list: pon_sum: {0}'.format(pon_sum))
  tn.read_until(b'\r', timeout=1)
  pon_list = []
  for i in range(0,int(pon_sum)):
    current_pon = tn.read_until(b' ,', timeout=1)[:-2].decode('utf-8')
    pon_list.append(current_pon)
    logger.debug('get_pon_list: pon_list finding loop: current_pon: {0}'.format(current_pon))
    waste_value = tn.read_until(b'\r', timeout=1).decode('utf-8')
    logger.debug('get_pon_list: pon_list finding loop: waste_value: {0}'.format(waste_value.replace('\r',' ')))
  logger.debug('get_pon_list: pon_list: {0}'.format(pon_list))
  waste_value = tn.read_until(b'gponline# ', timeout=1)
  logger.debug('get_pon_list: catch gponline#: {0}'.format(waste_value))
  tn.write(str_to_telnet('cd ..'))
  waste_value = tn.read_until(b'Admin# ', timeout=1)
  logger.debug('get_pon_list: catch Admin#: {0}'.format(waste_value))
  return pon_list

def logger_decorator(original_function):
  @wraps
  def wrapper(*args, **kwargs):
    logger.debug('args: ({0}) kwargs: ({1})'.format(args, kwargs))
    return original_function(*args, **kwargs)
  return wrapper

def sanitize_dumb(string):
  return string.replace(',',', ').replace('//','').replace(' /',', ').replace('\t','').replace(' ,',',').replace(' / ',', ').replace('  ',' ')

def sanitize_name(name):
  name = name.replace('*','').replace('0-','').replace('1-','').replace('2-','')
  if name[0] == ' ':
    name = name[1:]
  return name

def connect_su(tn):
  tn.read_until(b'Login: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.user))
  tn.read_until(b'Password: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.password))
  tn.read_until(b'User> ', timeout=1)
  tn.write(str_to_telnet('enable'))
  tn.read_until(b'Password: ', timeout=1)
  tn.write(str_to_telnet(telnet_config.password_sudo))
  tn.read_until(b'Admin# ', timeout=1)
  tn.write(str_to_telnet('cd service'))
  tn.read_until(b'service# ', timeout=1)
  tn.write(str_to_telnet('terminal length 512'))
  tn.read_until(b'service# ', timeout=1)
  tn.write(str_to_telnet('cd ..'))
  tn.read_until(b'Admin# ', timeout=1)

def disconnect_su(tn):
  tn.write(str_to_telnet('cd ..'))
  tn.read_until(b'Admin# ', timeout=1)
  tn.write(str_to_telnet('quit'))
  tn.close()

def get_next_value(tn, char):
  value = tn.read_until(char.encode('ascii'), timeout=1)
  logger.debug('get_next_value: first catch: {0}'.format(value[:-1]))
  while char.encode('ascii') in value[:-1] or char.encode('ascii') is value:
    value = tn.read_until(char.encode('ascii'), timeout=1)
    logger.debug('get_next_value: next catch: {0}'.format(value[:-1]))
  logger.debug('get_next_value: return: {0}'.format(value[:-1]))
  return value[:-1].decode('utf-8')

def is_int(s):
  try: 
    int(s)
    return True
  except ValueError:
    return False

def find_clients_by_onu(session, onu):
  logins = []
  login_usernames = []
  for associated_mac in onu.associated_mac_list:
    current_login_query = session.execute("SELECT DISTINCT UserName FROM {0} WHERE CallingStationID = :mac ORDER BY AcctStartTime DESC LIMIT 1;".format(config.mysql['radius_acct_table']), {'mac': associated_mac}).first()
    if current_login_query and current_login_query[0] not in login_usernames:
      login_usernames.append(current_login_query[0])
      logins.append(Login(session, onu, current_login_query[0]))
  logger.debug('find_clients_by_onu: logins found: {0}'.format(len(logins)))
  clients = []
  for login in logins:
    client_exist = False
    for client in clients:
      if client.client_id == login.client_id:
        if login not in client.logins:
          client.logins.append(login)
        client_exist = True
    if not client_exist:
      logger.debug('find_clients_by_onu: not yet existent client_id: {0}'.format(login.client_id))
      new_client = Client(session, login.client_id)
      new_client.logins.append(login)
      clients.append(new_client)
  return clients

def print_clients(clients):
  printed_clients = []
  printed_logins = []
  for client in clients:
    if client.cpf not in printed_clients:
      logger.info('\n{0}\n{1}\n{2}\n{3}'.format(client.name, client.cpf, client.address, 'Ativo' if client.enable else 'Bloqueado'))
      printed_clients.append(client.cpf)
    for login in client.logins:
      if login.username not in printed_logins:
        logger.info('\n{0} {1}\n{2} {3}\n{4} {5}\n{6} P{7} PON{8} ONU{9}{10} CLIENTE {11}\nVLAN: {12} Power: {13}\n{14}'.format(login.username, login.password, login.plan, 'Ativo' if login.enable else 'Bloqueado', login.ip, login.mac, login.onu.phy_address, login.onu.board, login.onu.pon, '0' if int(login.onu.onu_number) < 10 else '', login.onu.onu_number, login.username.upper(), login.onu.vlan, login.onu.signal_power, '\n'.join(login.onu.associated_mac_list)))
        printed_logins.append(login.username)

def find_onu_by_user(session, tn, username):
  login_query = session.execute("SELECT CallingStationID FROM {0} WHERE UserName = :username ORDER BY AcctStartTime DESC LIMIT 1;".format(config.mysql['radius_acct_table']), {'username': username}).first()
  if login_query:
    mac = login_query[0]
    onu = Onu(tn, mac=mac)
    login = Login(session, onu, username)
    client = Client(session, login.client_id)
    logger.info('\n{0}\n{1}\n{2}\n{3}'.format(client.name, client.cpf, client.address, 'Ativo' if client.enable else 'Bloqueado'))
    logger.info('\n{0} {1}\n{2} {3}\n{4} {5}\n{6} P{7} PON{8} ONU{9}{10} CLIENTE {11}\nVLAN: {12} Power: {13}\n{14}'.format(login.username, login.password, login.plan, 'Ativo' if login.enable else 'Bloqueado', login.ip, login.mac, login.onu.phy_address, login.onu.board, login.onu.pon, '0' if int(login.onu.onu_number) < 10 else '', login.onu.onu_number, login.username.upper(), login.onu.vlan, login.onu.signal_power, '\n'.join(login.onu.associated_mac_list)))

def find_onu_by_id(session, tn, onu_id):
  onu = Onu(tn, onu_id=onu_id)
  print_clients(find_clients_by_onu(session, onu))

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--user', dest='l', help='Usuario a ser consultado', default=None)
  parser.add_argument('-o', '--onu', dest='o', help='ONU a ser consultada', default=None)
  parser.add_argument('-i', '--id', dest='i', help='ID da ONU a ser consultada', default=None)
  args = parser.parse_args()

  login = None
  onu = None
  onu_id = None
  if args.l:
    login = str(args.l)
  elif args.o:
    onu = str(args.o)
  elif args.i:
    onu_id = str(args.i)

  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(config.mysql['username'], config.mysql['password'], config.mysql['host'], config.mysql['database']), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  
  with Telnet(telnet_config.ip, telnet_config.port) as tn:
    connect_su(tn)
    if onu: print_clients(find_clients_by_onu(session, Onu(tn, string=onu)))
    elif login: find_onu_by_user(session, tn, login)
    elif onu_id: find_onu_by_id(session, tn, onu_id)

if __name__ == '__main__':
  main()