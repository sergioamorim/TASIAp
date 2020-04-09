from datetime import timedelta, timezone
from inspect import stack
from re import search
from unicodedata import normalize

from telegram import MAX_MESSAGE_LENGTH


def is_query_update(update):
  try:
    update.message.chat
  except AttributeError:
    return True
  else:
    return False


def format_strhexoctet(strhexoctet):
  return strhexoctet.zfill(2).upper()


def hexstr_to_hexoctetstr(hexstr):
  if len(hexstr) > 2:
    return hexstr_to_hexoctetstr(hexstr[:-2]) + ' ' + format_strhexoctet(hexstr[-2:])
  return format_strhexoctet(hexstr[-2:])


def int_to_hexoctetstr(intvalue):
  return hexstr_to_hexoctetstr(format(int(intvalue), 'x'))


def assure_two_octet_hexstr(hexstr):
  if len(hexstr) == 2:
    return '00 ' + hexstr
  return hexstr


def get_onu_number_from_id(onu_id):
  return int(onu_id[2:])


def get_pon_id(onu_id):
  return onu_id[1:2]


def str_char_to_hex_octect(str_char):
  return hex(ord(str_char))[2:].upper()


def string_to_hex_octects(string, length):
  string_list = list(string)
  hex_list = list(map(str_char_to_hex_octect, string_list))
  hex_list.extend(['00']*(length-len(string_list)))
  return ' '.join(hex_list)


def generate_cvlan(board_id, pon_id):
  board_id_id = '1' if board_id == '12' else '2'
  return '{0}{1}00'.format(board_id_id, pon_id)


def get_board_id(onu_id):
  return '12' if onu_id[:1] == '1' else '14'


def is_onu_id_valid(onu_id):
  return is_int(onu_id) and 1100 < int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(
    onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9


def is_vlan_id_valid(vlan_id):
  return is_int(vlan_id) and 0 < int(vlan_id) < 4086


def is_serial_valid(serial):
  return search('([0-9A-Z]{4}[0-9A-Fa-f]{8})', serial) is not None


def remove_accents(string):
  return str(normalize('NFD', string).encode('ascii', 'ignore').decode('utf-8'))


def sanitize_dumb(string):
  return string.replace(',', ', ').replace('//', '').replace(' /', ', ').replace('\t', '').replace(' ,', ',').replace(
    ' / ', ', ').replace('  ', ' ')


def is_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


def get_caller_name():
  return stack()[2].function


def get_auth_onu_device_id(onu_device):
  board_id = '1' if onu_device.pon.board.board_id == '12' else '2'
  onu_number = onu_device.number if onu_device.number > 9 else '0{0}'.format(onu_device.number)
  return '{0}{1}{2}'.format(board_id, onu_device.pon.pon_id, onu_number)


def get_onu_id_from_cto_vlan_name(cto_vlan_name):
  board_id = '1' if cto_vlan_name[7:9] == '12' else '2'
  return '{0}{1}{2}'.format(board_id, cto_vlan_name[13:14], cto_vlan_name[18:20])


def get_cto_name_from_cto_vlan_name(cto_vlan_name):
  return cto_vlan_name[31:].replace('-', ' ')


def get_vlan_id_from_cto_vlan_name(cto_vlan_name):
  return cto_vlan_name[1:5]


def sanitize_cto_vlan_name(cto_vlan_name):
  if len(cto_vlan_name) > 32:
    onu_id = get_onu_id_from_cto_vlan_name(cto_vlan_name)
    cto_actual_name = get_cto_name_from_cto_vlan_name(cto_vlan_name)
    vlan_id = get_vlan_id_from_cto_vlan_name(cto_vlan_name)
    vlan_reference = '(v{0}) '.format(vlan_id) if vlan_id != onu_id else ''
    cto_sanitized_name = 'CTO {0} {1}{2}'.format(onu_id, vlan_reference, cto_actual_name)
    return cto_sanitized_name
  return ''


def format_datetime(datetime_object, safename=False, readable=False):
  if safename:
    datetime_format = '%Y-%m-%d_%H-%M-%S'
  elif readable:
    datetime_format = '%H:%M:%S de %d/%m/%Y'
  else:
    datetime_format = '%d/%m/%Y %H:%M:%S'
  return datetime_object.astimezone(timezone(timedelta(hours=-3))).strftime(datetime_format)


def format_onu_state(onu_state):
  return 'online' if onu_state == 'up' else 'offline'


def get_enable_emoji(enable):
  return '✅' if enable else '❌'


def get_status_emoji(status):
  if status == 1:
    return '🔹'
  if status == 2:
    return '💲'
  if status == 0:
    return '🚫'
  return '🔴'


def sanitize_name(name):
  if (dirty_prefix_pos := name.find('-')) != -1 and dirty_prefix_pos < 4:
    name = name[dirty_prefix_pos + 1:]
  if (dirty_prefix_pos := name.find('*')) != -1 and dirty_prefix_pos < 4:
    name = name[dirty_prefix_pos + 1:]
  name = name.replace('*', '').replace('0-', '').replace('1-', '').replace('2-', '')
  if name[0] == ' ':
    name = name[1:]
  return remove_accents(name).upper()


def format_clients_message(name, result):
  message = ''
  for client in result['direct']:
    message_addition = '{0} Nome: <u>{1}</u>\nEndereço: {2}, {3}\nPlano: {4}\n{5} <b>Usuário:</b> ' \
                       '<code>{6}</code>\n'.format(get_status_emoji(client['status']), client['nome'],
                                                   client['endereco'], client['numero'], client['groupname'],
                                                   get_enable_emoji(client['enable']), client['user'])
    if len(message) + len(message_addition) < MAX_MESSAGE_LENGTH - 18:
      message = message + message_addition
    else:
      return message + '\n\n<b>CROPED!</b>'
  message = message + '\n'
  for client in result['related']:
    message_addition = '{0} Nome: <u>{1}</u>\nEndereço: {2}, {3}\n'.format(get_status_emoji(client['status']),
                                                                           client['nome'], client['endereco'],
                                                                           client['numero'])
    if len(message) + len(message_addition) < MAX_MESSAGE_LENGTH - 18:
      message = message + message_addition
    else:
      return message + '\n\n<b>CROPED!</b>'
    name = remove_accents(name.lower())
    if name in client['complemento'].lower():
      message_addition = 'Complemento: {0}\n'.format(sanitize_dumb(client['complemento']))
      if len(message) + len(message_addition) < MAX_MESSAGE_LENGTH - 18:
        message = message + message_addition
      else:
        return message + '\n\n<b>CROPED!</b>'
    if name in client['referencia'].lower():
      message_addition = 'Referencia: {0}\n'.format(sanitize_dumb(client['referencia']))
      if len(message) + len(message_addition) < MAX_MESSAGE_LENGTH - 18:
        message = message + message_addition
      else:
        return message + '\n\n<b>CROPED!</b>'
    if name in client['observacao'].lower():
      message_addition = 'Observacao: {0}\n'.format(sanitize_dumb(client['observacao']))
      if len(message) + len(message_addition) < MAX_MESSAGE_LENGTH - 18:
        message = message + message_addition
      else:
        return message + '\n\n<b>CROPED!</b>'
    message_addition = 'Plano: {0}\n{1} <b>Usuário:</b> <code>{2}</code>\n'.format(client['groupname'],
                                                                                   get_enable_emoji(client['enable']),
                                                                                   client['user'])
    if len(message) + len(message_addition) < MAX_MESSAGE_LENGTH - 18:
      message = message + message_addition
    else:
      return message + '\n\n<b>CROPED!</b>'
  if len(message) > 1:
    return message
  return 'Nenhum cliente encontrado com o termo informado.'
