from argparse import ArgumentParser

from common.mysql_common import supply_mysql_session
from common.string_common import remove_accents, sanitize_dumb, sanitize_name
from logger import Log, get_logger

logger = get_logger(__name__)


def make_dict(clients):
  clients_dict = []
  for client in clients:
    d = dict(client.items())
    d['nome'] = sanitize_name(d['nome'])
    clients_dict.append(d)
  sorted_dict = sorted(clients_dict, key=lambda client_result: client_result['user'])
  return sorted(sorted_dict, key=lambda client_result: client_result['nome'])


@supply_mysql_session
@Log(logger)
def find_username_by_name(name, session=None):
  name = remove_accents(name.lower())
  clause = "SELECT nome, endereco, numero, complemento, referencia, observacao, status, user, pass, enable, " \
           "groupname FROM clientes INNER JOIN login ON clientes.id = login.cliente_id WHERE ((status = 1 OR status " \
           "= 2) AND enable = 1) AND nome LIKE :name OR endereco LIKE :name OR complemento LIKE :name OR referencia " \
           "LIKE :name OR observacao LIKE :name OR user LIKE :name ORDER BY nome;"
  if query_result := session.execute(clause=clause, params={'name': '%{name}%'.format(name=name)}):
    clients = []
    related_clients = []
    for client in make_dict(query_result):
      if name in client['nome'].lower() or name in client['user'].lower() or name in client['endereco'].lower():
        clients.append(client)
      else:
        related_clients.append(client)
    return {'direct': clients, 'related': related_clients}
  return None


def main():
  parser = ArgumentParser()
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
