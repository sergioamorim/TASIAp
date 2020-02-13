#!/usr/bin/env python3.8
# coding=utf-8

import argparse
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysqldb_config
import unicodedata

logger = logging.getLogger('username_by_name')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/username_by_name.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def remove_accents(string):
  return str(unicodedata.normalize('NFD', string).encode('ascii', 'ignore').decode('utf-8'))

def sanitize_name(name):
  if (dirty_prefix_pos := name.find('-')) != -1 and dirty_prefix_pos < 4:
    name = name[dirty_prefix_pos+1:]
  if (dirty_prefix_pos := name.find('*')) != -1 and dirty_prefix_pos < 4:
    name = name[dirty_prefix_pos+1:]
  name = name.replace('*','').replace('0-','').replace('1-','').replace('2-','')
  if name[0] == ' ':
    name = name[1:]
  return remove_accents(name).upper()

def sanitize_dumb(string):
  return string.replace(',',', ').replace('//','').replace(' /',', ').replace('\t','').replace(' ,',',').replace(' / ',', ').replace('  ',' ')

def make_dict(clientes):
  clientes_dict = []
  for cliente in clientes:
    d = dict(cliente.items())
    d['nome'] = sanitize_name(d['nome'])
    clientes_dict.append(d)
  sorted_dict = sorted(clientes_dict, key=lambda cliente : cliente['user'])
  return sorted(sorted_dict, key=lambda cliente : cliente['nome'])

def find_username_by_name(name):
  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host, mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  session = Session()
  query_string = "SELECT nome, endereco, numero, complemento, referencia, observacao, status, user, pass, enable, groupname FROM {0} INNER JOIN {1} ON {0}.id = {1}.cliente_id WHERE ((status = 1 OR status = 2) AND enable = 1) AND nome LIKE '%{2}%' OR endereco LIKE '%{2}%' OR complemento LIKE '%{2}%' OR referencia LIKE '%{2}%' OR observacao LIKE '%{2}%' OR user LIKE '%{2}%' ORDER BY nome ASC;".format(mysqldb_config.clientes_table, mysqldb_config.login_table, name)
  if (query_result := session.execute(query_string)):
    for cliente in make_dict(query_result):
      print('Nome: {0}\nEndereço: {1}, {2}'.format(cliente['nome'], cliente['endereco'], cliente['numero']))
      if name not in cliente['nome'].lower() and name not in cliente['user'].lower() and name not in cliente['endereco'].lower():
        if name in cliente['complemento'].lower():
          print('Complemento: {0}'.format(sanitize_dumb(cliente['complemento'])))
        elif name in cliente['referencia'].lower():
          print('Referencia: {0}'.format(sanitize_dumb(cliente['referencia'])))
        elif name in cliente['observacao'].lower():
          print('Observacao: {0}'.format(sanitize_dumb(cliente['observacao'])))
      print('Usuario: {0}'.format(cliente['user']))
  return None

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-n', '--name', dest='n', help='Nome do cliente a ser consultado.', default=None)
  args = parser.parse_args()

  if (name := args.n):
    print(find_username_by_name(remove_accents(name.lower())))
    return 0

  print('Informe o nome do cliente.')
  return 1

if __name__ == '__main__':
  main()