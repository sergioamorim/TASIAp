from os.path import dirname
from subprocess import run

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import testing_config, mysqldb_config


def run_mysql_cmd(mysql_cmd_opts):
  mysql_cmd = '{mysql_client} -h {host} -P {port} -u {username} -p{password}'.format(
    mysql_client=testing_config.mysql_client_binary_path,
    host=mysqldb_config.host, port=mysqldb_config.port,
    username=testing_config.mysql_sudo_username, password=testing_config.mysql_sudo_password)
  command = '{mysql_cmd} {mysql_cmd_opts}'.format(mysql_cmd=mysql_cmd, mysql_cmd_opts=mysql_cmd_opts)
  run(args=command, shell=True, check=True)


def create_testing_database():
  mysql_cmd_opts = '-e "DROP DATABASE IF EXISTS {database};CREATE DATABASE {database} DEFAULT CHARACTER SET ' \
                   'latin1;"'.format(database=mysqldb_config.database)
  run_mysql_cmd(mysql_cmd_opts=mysql_cmd_opts)


def setup_testing_database_structure():
  path = dirname(__file__)
  mysql_cmd_opts = '{database} < ' \
                   '{path}/data/myauth_admin_database_structure.sql'.format(path=path, database=mysqldb_config.database)
  run_mysql_cmd(mysql_cmd_opts=mysql_cmd_opts)


def get_sudo_session():
  sudo_engine_parameters = 'mysql://{username}:{password}@{host}:{port}/{database}'.format(
    username=testing_config.mysql_sudo_username, password=testing_config.mysql_sudo_password, host=mysqldb_config.host,
    port=mysqldb_config.port, database=mysqldb_config.database)
  engine = create_engine(sudo_engine_parameters, encoding='latin1')
  session_maker = sessionmaker(bind=engine)
  return session_maker()


def create_ordinary_user(sudo_session):
  clause = 'DROP USER IF EXISTS :username@:host;'
  username_and_host_params = {'username': mysqldb_config.username, 'host': mysqldb_config.host}
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'CREATE USER :username@:host IDENTIFIED BY :password;'
  params = {'username': mysqldb_config.username, 'host': mysqldb_config.host, 'password': mysqldb_config.password}
  sudo_session.execute(clause=clause, params=params)

  clause = 'GRANT INSERT, DELETE ON {database}.login_radius TO ' \
           ':username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'GRANT UPDATE (pass, mac, proxy, radsyncframedip, radsyncmac, radsyncsim, radsyncmkurl, radnas_id, ' \
           'accesspoint) ON {database}.login TO :username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'GRANT SELECT (cliente_id, user, ip, groupname, enable, info, pass) ON {database}.login TO ' \
           ':username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'GRANT SELECT (AcctStopTime, AcctStartTime, CalledStationId, CallingStationId, FramedIPAddress, UserName) ' \
           'ON {database}.radius_acct TO :username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'GRANT SELECT (CalledStationId, CallingStationId, sucess, pass, user) ON {database}.radius_postauth TO ' \
           ':username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'GRANT SELECT (timestamp, info, console) ON {database}.admlog TO ' \
           ':username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)

  clause = 'GRANT SELECT (observacao, referencia, complemento, numero, endereco, sexo, nome, status, id) ON ' \
           '{database}.clientes TO :username@:host;'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause, params=username_and_host_params)


def drop_testing_database(sudo_session):
  clause = 'DROP DATABASE IF EXISTS {database};'.format(database=mysqldb_config.database)
  sudo_session.execute(clause=clause)


def drop_ordinary_user(sudo_session):
  clause = 'DROP USER IF EXISTS :username@:host;'
  params = {'username': mysqldb_config.username, 'host': mysqldb_config.host}
  sudo_session.execute(clause=clause, params=params)


def setup_mysql_testing_environment():
  mysqldb_config.database = 'test_{database}'.format(database=mysqldb_config.database)
  mysqldb_config.username = 'test_{username}'.format(username=mysqldb_config.username)
  create_testing_database()
  setup_testing_database_structure()
  sudo_session = get_sudo_session()
  create_ordinary_user(sudo_session=sudo_session)
  return sudo_session


def close_sudo_session(sudo_session):
  sudo_session.commit()
  sudo_session.close()


def shutdown_mysql_testing_environment(sudo_session):
  drop_ordinary_user(sudo_session=sudo_session)
  drop_testing_database(sudo_session=sudo_session)
  close_sudo_session(sudo_session=sudo_session)
