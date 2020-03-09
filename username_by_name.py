#!/usr/bin/env python3.8
# coding=utf-8

import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysqldb_config
from string_common import remove_accents, sanitize_dumb


def sanitize_name(name):
  if (dirty_prefix_pos := name.find('-')) != -1 and dirty_prefix_pos < 4:
    name = name[dirty_prefix_pos + 1:]
  if (dirty_prefix_pos := name.find('*')) != -1 and dirty_prefix_pos < 4:
    name = name[dirty_prefix_pos + 1:]
  name = name.replace('*', '').replace('0-', '').replace('1-', '').replace('2-', '')
  if name[0] == ' ':
    name = name[1:]
  return remove_accents(name).upper()


def make_dict(clients):
  clients_dict = []
  for client in clients:
    d = dict(client.items())
    d['nome'] = sanitize_name(d['nome'])
    clients_dict.append(d)
  sorted_dict = sorted(clients_dict, key=lambda client_result: client_result['user'])
  return sorted(sorted_dict, key=lambda client_result: client_result['nome'])


def find_username_by_name(name):
  engine = create_engine(
    'mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host,
                                     mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  name = remove_accents(name.lower())
  query_string = "SELECT nome, endereco, numero, complemento, referencia, observacao, status, user, pass, enable, " \
                 "groupname FROM {0} INNER JOIN {1} ON {0}.id = {1}.cliente_id WHERE ((status = 1 OR status = 2) AND " \
                 "enable = 1) AND nome LIKE '%{2}%' OR endereco LIKE '%{2}%' OR complemento LIKE '%{2}%' OR " \
                 "referencia LIKE '%{2}%' OR observacao LIKE '%{2}%' OR user LIKE '%{2}%' ORDER BY nome ASC;".format(
                  mysqldb_config.clientes_table, mysqldb_config.login_table, name)
  final_result = None
  if query_result := session.execute(query_string):
    clients = []
    related_clients = []
    for client in make_dict(query_result):
      if name in client['nome'].lower() or name in client['user'].lower() or name in client['endereco'].lower():
        clients.append(client)
      else:
        related_clients.append(client)
    final_result = {'direct': clients, 'related': related_clients}
  return final_result


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-n', '--name', dest='n', help='Nome do cliente a ser consultado.', default=None)
  args = parser.parse_args()

  if name := args.n:
    result = find_username_by_name(name)
    for client in result['direct']:
      print('Nome: {0}\nEndereço: {1}, {2}\nUsuario: {3}'.format(client['nome'], client['endereco'], client['numero'],
                                                                 client['user']))
    for client in result['related']:
      print('Nome: {0}\nEndereço: {1}, {2}'.format(client['nome'], client['endereco'], client['numero']))
      name = remove_accents(name.lower())
      if name in client['complemento'].lower():
        print('Complemento: {0}'.format(sanitize_dumb(client['complemento'])))
      if name in client['referencia'].lower():
        print('Referencia: {0}'.format(sanitize_dumb(client['referencia'])))
      if name in client['observacao'].lower():
        print('Observacao: {0}'.format(sanitize_dumb(client['observacao'])))
      print('Usuario: {0}'.format(client['user']))
    return 0

  print('Informe o nome do cliente.')
  return 1


if __name__ == '__main__':
  main()
