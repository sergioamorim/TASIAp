import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from fpdf import FPDF
from requests import post
from os import remove
import mysqldb_config
import bot_config


def to_int(string):
  try:
    integer = int(string)
  except ValueError:
    integer = None
  return integer


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


def sanitize_name(name):
  name = name.replace('*', '').replace('0-', '').replace('1-', '').replace('2-', '')
  if name[0] == ' ':
    name = name[1:]
  return name


def sanitize_to_terminal(string):
  return string.replace(chr(0xC2), '\xC3\x82').replace(chr(0xA0), '').replace(chr(0xC3), '\xC3\x83').replace(chr(0xBA),
                                                                                                             '\xC2\xBA').replace(
    chr(0xD3), '\xC3\x93').replace(chr(0xC7), '\xC3\x87'
                                   ).replace(chr(0xD5), '\xC3\x95').replace(chr(0xC9), '\xC3\x89').replace(chr(0xAA),
                                                                                                           '\xC2\xAA').replace(
    chr(0xD4), '\xC3\x94').replace(chr(0xED), '\xC3\xAD').replace(chr(0xCD), '\xC3\x8D'
                                                                  ).replace(chr(0xC0), '\xC3\x80').replace(chr(0xC1),
                                                                                                           '\xC3\x81').replace(
    chr(0xB0), '\xC2\xB0').replace(chr(0xE2), '\xC3\xA2').replace(chr(0xCA), '\xC3\x8A').replace(chr(0xE9), '\xC3\xA9'
                                                                                                 ).replace(chr(0xEA),
                                                                                                           '\xC3\xAA').replace(
    chr(0xDA), '\xC3\x9A').replace(chr(0xE1), '\xC3\xA1').replace(chr(0xF3), '\xC3\xB3').replace(chr(0xF4),
                                                                                                 '\xC3\xB4').replace(
    chr(0xE3), '\xC3\xA3'
  ).replace(chr(0xFA), '\xC3\xBA').replace(chr(0xE7), '\xC3\xA7').replace(chr(0xB4), '\xC2\xB4')


def get_clientes_dict(users):
  if users:
    clientes_dict = []
    clientes = session.execute('SELECT clientes.nome, clientes.endereco, clientes.numero, clientes.complemento, '
                               'clientes.referencia, login.user FROM clientes INNER JOIN login ON clientes.id = '
                               'login.cliente_id WHERE clientes.status = 1 AND login.user IN ({0})'.format(
      str(users)[1:-1]))
    for cliente in clientes:
      d = dict(cliente.items())
      d['nome'] = sanitize_name(d['nome'])
      clientes_dict.append(d)
    clientes_dict = sorted(clientes_dict, key=get_nome)
    return clientes_dict
  return None


def plural_s(count):
  return 's' if count > 1 else ''


parser = argparse.ArgumentParser()

parser.add_argument("-c", "--cto", dest="c", help="Codigo da CTO a consultar")
parser.add_argument("-t", "--tecnico", dest="t", help="Ordenar clientes de acordo com endereço no PDF")

args = parser.parse_args()
cto = str(args.c)

if cto:
  engine = create_engine(
    'mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host,
                                     mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  row_cto_name = session.execute(
    'SELECT CalledStationId FROM radius_acct WHERE CalledStationId LIKE :cto ORDER BY AcctStartTime DESC LIMIT 1',
    {'cto': '%{0}%'.format(cto)}).first()
  usernames = session.execute(
    'SELECT DISTINCT UserName FROM radius_acct WHERE CalledStationId LIKE :cto AND UserName IN (SELECT user FROM '
    'login WHERE cliente_id IN (SELECT id FROM clientes WHERE status = 1))',
    {'cto': '%{0}%'.format(cto)})
  rows = []
  for username in usernames:
    last_cto = session.execute(
      'SELECT CalledStationId FROM radius_acct WHERE UserName = :username ORDER BY AcctStartTime DESC LIMIT 1',
      {'username': username[0]}).first()[0]
    if cto in last_cto:
      row = session.execute(
        'SELECT UserName, AcctStartTime, AcctStopTime FROM radius_acct WHERE UserName = :username ORDER BY '
        'AcctStartTime DESC LIMIT 1',
        {'username': username[0]}).first()
      rows.append(row)
  sorted_rows = sorted(rows, key=get_acct_stop_time, reverse=True)
  users_offline = []
  users_online = []
  for row in sorted_rows:
    if row['AcctStopTime'] is None:
      users_online.append(row['UserName'])
    else:
      users_offline.append(row['UserName'])
  users_offline_count = len(users_offline)
  users_online_count = len(users_online)
  if users_offline:
    clientes_offline_dict = get_clientes_dict(users_offline)
  if users_online:
    clientes_online_dict = get_clientes_dict(users_online)
  cto_name = row_cto_name['CalledStationId']
  cto_number, cto_legible_name = cto_name[1:5], cto_name[30:].replace('-', ' ')
  datetime_now = datetime.now()
  pdf = FPDF(format='a3')
  pdf.add_page(orientation='L')
  pdf.add_font('Calibri', '', 'fonts/CALIBRI.TTF', uni=True)
  pdf.add_font('Calibri', 'B', 'fonts/CALIBRIB.TTF', uni=True)
  effective_page_width = pdf.w - pdf.l_margin * pdf.r_margin
  pdf.set_font('Calibri', '', 13)
  pdf.write(0, 'CTO ')
  pdf.set_font('Calibri', 'B', 13)
  pdf.write(0, cto_number)
  pdf.set_font('Calibri', '', 13)
  pdf.write(0, cto_legible_name)
  pdf.set_font('Calibri', '', 9)
  pdf.write(0, '                Relatório gerado às {0} de {1}'.format(datetime_now.strftime('%H:%M:%S'),
                                                                       datetime_now.strftime('%d/%m/%Y')))
  pdf.ln(5)
  total_users_count = users_online_count + users_offline_count
  if users_offline_count and users_offline_count != total_users_count:
    pdf.write(0, '{0} cliente{1} offline de um total de {2} cliente{3} ({4} cliente{5} online).'.format(
      users_offline_count, plural_s(users_offline_count), total_users_count, plural_s(total_users_count),
      users_online_count, plural_s(users_online_count)))
  elif users_offline_count > 1 and not users_online_count:
    pdf.write(0, 'Todos os {0} clientes offline.'.format(users_offline_count))
  elif users_offline_count and not users_online_count:
    pdf.write(0, 'O \xC3\xBAnico cliente da ONU est\xC3\xA1 offline.')
  elif not users_offline_count and users_online_count > 1:
    pdf.write(0, 'Todos os {0} cliente{1} online.'.format(users_online_count, plural_s(users_online_count)))
  elif not users_offline_count and users_online_count:
    pdf.write(0, 'O \xC3\xBAnico cliente da ONU est\xC3\xA1 online.')
  pdf.ln(6)
  pdf.set_font('Calibri', '', 11)
  if users_offline:
    pdf.write(0, 'Clientes offline: {0}'.format(users_offline_count))
    pdf.ln(4)
    if args.t:
      sorted_dict = sorted(clientes_offline_dict, key=get_rua)
    else:
      sorted_dict = sorted(clientes_offline_dict, key=get_nome)
    pdf.set_font('Calibri', '', 9)
    for cliente in sorted_dict:
      pdf.write(0,
                '{0} - {1}, {2} {3} {4} Usuário: {5}'.format(get_nome(cliente), get_rua(cliente), get_numero(cliente),
                                                             sanitize_dumb(cliente['complemento']),
                                                             sanitize_dumb(cliente['referencia']), cliente['user']))
      pdf.ln(3)
  else:
    pdf.write(0, 'Nenhum cliente offline.')
    pdf.ln(3)
  pdf.set_font('Calibri', '', 11)
  pdf.set_text_color(120, 120, 120)
  pdf.ln(3)
  if users_online:
    pdf.write(0, 'Clientes online: {0}'.format(users_online_count))
    pdf.ln(4)
    if args.t:
      sorted_dict = sorted(clientes_online_dict, key=get_numero)
      sorted_dict = sorted(sorted_dict, key=get_rua)
    else:
      sorted_dict = sorted(clientes_online_dict, key=get_nome)
    pdf.set_font('Calibri', '', 9)
    for cliente in sorted_dict:
      pdf.write(0,
                '{0} - {1}, {2} {3} {4} Usuário: {5}'.format(get_nome(cliente), get_rua(cliente), get_numero(cliente),
                                                             sanitize_dumb(cliente['complemento']),
                                                             sanitize_dumb(cliente['referencia']), cliente['user']))
      pdf.ln(3)
  else:
    pdf.write(0, 'Nenhum cliente online.')
    pdf.ln(4)
  filename = 'rel-cto_{0}-{1}_{2}.pdf'.format(cto_number, cto_legible_name[1:].lower().replace(' ', '-'),
                                              datetime_now.strftime('%Y-%m-%d_%H-%M-%S'))
  pdf.output(filename, 'F')
  with open(filename, 'rb') as document:
    post('https://api.telegram.org/bot{0}/sendDocument'.format(bot_config.token),
         data={'chat_id': bot_config.default_chat}, files={'document': document})
  remove(filename)
