from contextlib import contextmanager
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.string_common import is_int
from config import mysqldb_config, bot_config
from logger import get_logger

logger = get_logger(__name__)


def supply_mysql_session(function):
  @wraps(function)
  def mysql_session_supplier(*args, **kwargs):
    if 'session' not in kwargs:
      with mysql_session() as session:
        return function(session=session, *args, **kwargs)
    return function(*args, **kwargs)
  return mysql_session_supplier


@contextmanager
def mysql_session():
  engine_parameters = 'mysql://{0}:{1}@{2}:{3}/{4}'.format(mysqldb_config.username, mysqldb_config.password,
                                                           mysqldb_config.host, mysqldb_config.port,
                                                           mysqldb_config.database)
  engine = create_engine(engine_parameters, encoding='latin1')
  session_maker = sessionmaker(bind=engine)
  session = session_maker()
  try:
    yield session
  finally:
    session.commit()
    session.close()


def user_exists(session, user):
  return session.execute('SELECT user FROM login WHERE user = :user;', {'user': user}).scalar()


def insert_into_radius_login(session, rtype, username, attribute, op, value):
  query_string = "INSERT INTO {0} (type, user, attribute, op, value, enable) VALUES ('{1}', '{2}', '{3}', '{4}', "
  if is_int(value):
    query_string = query_string + '{5}'
  else:
    query_string = query_string + "'{5}'"
  query_string = query_string + ', 1);'
  session.execute(query_string.format(mysqldb_config.login_radius_table, rtype, username, attribute, op, value))


def reauthorize_user(session, username):
  session.execute(
    "UPDATE {0} SET mac = '', proxy = '', radsyncframedip = 0, radsyncmac = 0, radsyncsim = 0, radsyncmkurl = 0, "
    "radnas_id = 0, accesspoint = 0 WHERE user = :username;".format(
      mysqldb_config.login_table), {'username': username})
  session.execute('DELETE FROM {0} WHERE user = :username;'.format(mysqldb_config.login_radius_table),
                  {'username': username})
  login_info = session.execute('SELECT ip, pass FROM {0} WHERE user = :username'.format(mysqldb_config.login_table),
                               {'username': username}).first()
  insert_into_radius_login(session, 'C', username, 'Simultaneous-Use', ':=', 1)
  insert_into_radius_login(session, 'C', username, 'User-Password', ':=', login_info['pass'])
  if login_info['ip']:
    insert_into_radius_login(session, 'R', username, 'Framed-IP-Address', '==', login_info['ip'])


@supply_mysql_session
def generate_pppoe_login_password(username, session=None):
  sql_query = 'SELECT user FROM {0} WHERE user = :username;'.format(mysqldb_config.login_table)
  if session.scalar(sql_query, {'username': username}):
    sql_query = 'UPDATE {0} SET pass = :password WHERE user = :username'.format(mysqldb_config.login_table)
    session.execute(sql_query, {'username': username, 'password': bot_config.default_pppoe_login_password})
    return bot_config.default_pppoe_login_password
  logger.error('generate_pppoe_login_password: user {0} not found').format(username)
  return None


@supply_mysql_session
def get_login_password(username, session=None):
  sql_query = 'SELECT pass FROM {0} WHERE user = :username;'.format(mysqldb_config.login_table)
  if login_password := session.scalar(sql_query, {'username': username}):
    return login_password.replace('=3F', '?')
  return generate_pppoe_login_password(username, session=session)
