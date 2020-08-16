from argparse import ArgumentParser
from datetime import datetime
from os import remove
from re import match

from fpdf import FPDF
from requests import post

from config import bot_config
from tasiap.common.mysql_common import supply_mysql_session
from tasiap.common.string_common import sanitize_name, sanitize_cto_vlan_name, format_datetime, get_board_id, \
  get_pon_id, is_vlan_id_valid


def get_acct_stop_time(result_row):
  if result_row['AcctStopTime']:
    return result_row['AcctStopTime']
  return datetime(1970, 1, 1, 0, 0, 0)


def get_nome(result_row):
  return result_row['nome']


def get_rua(result_row):
  return result_row['endereco']


def get_numero(result_row):
  return result_row['numero']


def sanitize_dumb(string):
  return string.replace(',', ', ').replace('//', '').replace(' /', ', ').replace('\t', '').replace(' ,', ',').replace(
    ' / ', ', ').replace('  ', ' ')


@supply_mysql_session
def get_clientes_dict(users, session=None):
  if users:
    clientes_dict = []
    clientes = session.execute(clause='SELECT clientes.nome, clientes.endereco, clientes.numero, clientes.complemento, '
                               'clientes.referencia, login.user FROM clientes INNER JOIN login ON clientes.id = '
                               'login.cliente_id WHERE clientes.status = 1 AND login.user IN :users',
                               params={'users': users})
    for cliente in clientes:
      d = dict(cliente.items())
      d['nome'] = sanitize_name(d['nome'])
      clientes_dict.append(d)
    clientes_dict = sorted(clientes_dict, key=get_nome)
    return clientes_dict
  return None


def plural_s(count):
  return 's' if count > 1 else ''


def is_pon_id(cto_id):
  if match('[1-3][1-9]00', cto_id):
    return True
  return False


@supply_mysql_session
def get_cto_name(cto_id, session=None):
  if is_pon_id(cto_id):
    board_id = get_board_id(cto_id)
    pon_id = get_pon_id(cto_id)
    return 'Placa {0} PON {1}'.format(board_id, pon_id)
  clause = 'SELECT CalledStationId FROM radius_acct WHERE CalledStationId LIKE :cto ORDER BY AcctStartTime DESC LIMIT 1'
  if cto_name := session.scalar(clause=clause, params={'cto': '%{cto_id}%'.format(cto_id=cto_id)}):
    if sanitized_cto_name := sanitize_cto_vlan_name(cto_name):
      return sanitized_cto_name
  return cto_id


@supply_mysql_session
def get_usernames(cto_id, session=None):
  clause = 'SELECT DISTINCT UserName FROM radius_acct WHERE CalledStationId LIKE :cto AND UserName IN (SELECT user ' \
          'FROM login WHERE cliente_id IN (SELECT id FROM clientes WHERE status = 1))'
  if usernames := session.execute(clause=clause, params={'cto': '%{cto_id}%'.format(cto_id=cto_id)}):
    return usernames
  return None


@supply_mysql_session
def get_last_cto(username, session=None):
  clause = 'SELECT CalledStationId FROM radius_acct WHERE UserName = :username ORDER BY AcctStartTime DESC LIMIT 1'
  if len(username):
    if last_cto := session.scalar(clause=clause, params={'username': username[0]}):
      return last_cto
  return None


@supply_mysql_session
def get_connection_info(username, session=None):
  query = 'SELECT UserName, AcctStartTime, AcctStopTime FROM radius_acct WHERE UserName = :username ORDER BY ' \
          'AcctStartTime DESC LIMIT 1'
  if len(username):
    if connection_info := session.execute(query, {'username': username[0]}).first():
      return connection_info
  return None


@supply_mysql_session
def get_connections_info(cto_id, session=None):
  usernames = get_usernames(cto_id, session=session)
  connections_info = []
  for username in usernames:
    last_cto = get_last_cto(username, session=session)
    if cto_id in last_cto:
      connection_info = get_connection_info(username, session=session)
      connections_info.append(connection_info)
  ordered_connections_info = sorted(connections_info, key=get_acct_stop_time, reverse=True)
  return ordered_connections_info


@supply_mysql_session
def get_clients(cto_id, session=None):
  connections_info = get_connections_info(cto_id, session=session)
  online = []
  offline = []
  for connection_info in connections_info:
    if connection_info['AcctStopTime'] is None:
      online.append(connection_info['UserName'])
    else:
      offline.append(connection_info['UserName'])
  online_dict = get_clientes_dict(online)
  offline_dict = get_clientes_dict(offline)
  return {'online': online_dict, 'offline': offline_dict}


def get_report_summary(users_online_count, users_offline_count):
  total_users_count = users_online_count + users_offline_count
  if users_offline_count and users_offline_count != total_users_count:
    return '{0} cliente{1} offline de um total de {2} cliente{3} ({4} cliente{5} online).'.format(
            users_offline_count, plural_s(users_offline_count), total_users_count, plural_s(total_users_count),
            users_online_count, plural_s(users_online_count))
  elif users_offline_count > 1 and not users_online_count:
    return 'Todos os {0} clientes offline.'.format(users_offline_count)
  elif users_offline_count and not users_online_count:
    return 'O único cliente está offline.'
  elif not users_offline_count and users_online_count > 1:
    return 'Todos os {0} cliente{1} online.'.format(users_online_count, plural_s(users_online_count))
  elif not users_offline_count and users_online_count:
    return 'O único cliente está online.'
  else:
    return 'Nenhum cliente encontrado.'


def get_time_generated_phrase(datetime_obj):
  return ' '*16 + 'Relatório gerado às {0}'.format(format_datetime(datetime_obj, readable=True))


def get_filename(cto_name, datetime_obj):
  return 'rel-{0}-{1}.pdf'.format(cto_name.lower().replace(' ', '-'), format_datetime(datetime_obj, safename=True))


def get_clients_count(clients):
  if not clients:
    return 0
  return len(clients)


def get_pdf_page():
  pdf = FPDF(format='a3')
  pdf.add_page(orientation='L')
  pdf.add_font('Calibri', '', 'fonts/CALIBRI.TTF', uni=True)
  pdf.add_font('Calibri', 'B', 'fonts/CALIBRIB.TTF', uni=True)
  pdf.set_font('Calibri', '', 13)
  return pdf


def write_client_info_line(cliente, pdf):
  pdf.write(0,
            '{0} - {1}, {2} {3} {4} Usuário: {5}'.format(get_nome(cliente), get_rua(cliente), get_numero(cliente),
                                                         sanitize_dumb(cliente['complemento']),
                                                         sanitize_dumb(cliente['referencia']), cliente['user']))
  pdf.ln(3)


@supply_mysql_session
def do_things(cto_id, tech_report, session=None):
  now = datetime.now()
  cto_name = get_cto_name(cto_id, session=session)
  clients = get_clients(cto_id, session=session)
  users_online_count = get_clients_count(clients['online'])
  users_offline_count = get_clients_count(clients['offline'])
  pdf = get_pdf_page()
  pdf.write(0, cto_name)
  pdf.set_font('Calibri', '', 9)
  pdf.write(0, get_time_generated_phrase(now))
  pdf.ln(5)
  pdf.write(0, get_report_summary(users_online_count, users_offline_count))
  pdf.ln(6)
  pdf.set_font('Calibri', '', 11)
  if clients['offline']:
    pdf.write(0, 'Clientes offline: {0}'.format(users_offline_count))
    pdf.ln(4)
    if tech_report:
      sorted_dict = sorted(clients['offline'], key=get_rua)
    else:
      sorted_dict = sorted(clients['offline'], key=get_nome)
    pdf.set_font('Calibri', '', 9)
    for cliente in sorted_dict:
      write_client_info_line(cliente=cliente, pdf=pdf)
  else:
    pdf.write(0, 'Nenhum cliente offline.')
    pdf.ln(3)
  pdf.set_font('Calibri', '', 11)
  pdf.set_text_color(120, 120, 120)
  pdf.ln(3)
  if clients['online']:
    pdf.write(0, 'Clientes online: {0}'.format(users_online_count))
    pdf.ln(4)
    if tech_report:
      sorted_dict = sorted(clients['online'], key=get_numero)
      sorted_dict = sorted(sorted_dict, key=get_rua)
    else:
      sorted_dict = sorted(clients['online'], key=get_nome)
    pdf.set_font('Calibri', '', 9)
    for cliente in sorted_dict:
      write_client_info_line(cliente=cliente, pdf=pdf)
  else:
    pdf.write(0, 'Nenhum cliente online.')
    pdf.ln(4)
  filename = get_filename(cto_name, now)
  pdf.output(filename, 'F')
  with open(filename, 'rb') as document:
    post('https://api.telegram.org/bot{0}/sendDocument'.format(bot_config.token),
         data={'chat_id': bot_config.default_chat}, files={'document': document})
  remove(filename)


def main():
  parser = ArgumentParser()
  parser.add_argument("-c", "--cto", dest="c", help="Código da CTO a consultar")
  parser.add_argument("-t", "--tecnico", dest="t", help="Ordenar clientes de acordo com endereço no PDF")
  args = parser.parse_args()

  if args.c:
    if is_vlan_id_valid(args.c):
      do_things(args.c, args.t)
      return 0
    print('Código inválido.')
    return 1

  print('Informe o código da CTO.')
  return 1


if __name__ == '__main__':
  main()
