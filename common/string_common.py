from inspect import stack
from re import findall, search
from unicodedata import normalize

from telegram import MAX_MESSAGE_LENGTH


def is_onu_id_valid(onu_id):
  return is_int(onu_id) and 1100 < int(onu_id) < 3900 and int(onu_id[2:]) > 0 and int(
    onu_id[1:2]) > 0 and int(onu_id[1:2]) < 9


def is_vlan_id_valid(vlan_id):
  return is_int(vlan_id) and 0 < int(vlan_id) < 4096


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


def get_onu_id_from_repr(onu_repr):
  onu_repr_pattern = "([0-9])',board='<Board\(board_id='([0-9]{2})'\)>',last_authorized_onu_number='[0-9]+'\)>'," \
                     "onu_type='.*',number='([0-9]+)"
  regex_result = findall(onu_repr_pattern, onu_repr)
  board = regex_result[0][1]
  pon = regex_result[0][0]
  onu_number = regex_result[0][2]
  onu_id = '{0}{1}{2}{3}'.format('1' if board == '12' else '2', pon, '0' if int(onu_number) < 10 else '', onu_number)
  return onu_id


def sanitize_cto_vlan_name(cto_vlan_name):
  if len(cto_vlan_name) > 32:
    board_id = '1' if cto_vlan_name[7:9] == '12' else '2'
    onu_id = '{0}{1}{2}'.format(board_id, cto_vlan_name[13:14], cto_vlan_name[18:20])
    cto_actual_name = cto_vlan_name[31:].replace('-', ' ')
    vlan = '({0}) '.format(cto_vlan_name[:5]) if cto_vlan_name[1:5] != onu_id else ''
    cto_sanitized_name = 'CTO {0} {1}{2}'.format(onu_id, vlan, cto_actual_name)
    return cto_sanitized_name
  return ''


def format_datetime(datetime_object):
  return datetime_object.strftime('%d/%m/%Y %H:%M:%S')


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
