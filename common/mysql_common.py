from contextlib import contextmanager
from functools import wraps
from inspect import signature

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import mysqldb_config, bot_config
from logger import get_logger

logger = get_logger(__name__)


def supply_mysql_session(function):
  @wraps(function)
  def mysql_session_supplier(*args, **kwargs):
    available_args = signature(function).parameters.keys()
    if 'mysql_session' in available_args:
      if 'mysql_session' not in kwargs:
        with mysql_session_factory() as mysql_session:
          return function(mysql_session=mysql_session, *args, **kwargs)
    elif 'session' in available_args:
      if 'session' not in kwargs:
        with mysql_session_factory() as mysql_session:
          return function(session=mysql_session, *args, **kwargs)
    return function(*args, **kwargs)
  return mysql_session_supplier


@contextmanager
def mysql_session_factory():
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
  clause = "INSERT INTO login_radius (type, user, attribute, op, value, enable) VALUES (:rtype, :username, " \
           ":attribute, :op, :value, 1);"
  params = {'rtype': rtype, 'username': username, 'attribute': attribute, 'op': op, 'value': value}
  session.execute(clause=clause, params=params)


def reauthorize_user(session, username):
  session.execute(
    clause="UPDATE login SET mac = '', proxy = '', radsyncframedip = 0, radsyncmac = 0, radsyncsim = 0, radsyncmkurl = "
           "0, radnas_id = 0, accesspoint = 0 WHERE user = :username;", params={'username': username})
  session.execute(clause='DELETE FROM login_radius WHERE user = :username;', params={'username': username})
  login_info = session.execute(clause='SELECT ip, pass FROM login WHERE user = :username',
                               params={'username': username}).first()
  insert_into_radius_login(session, 'C', username, 'Simultaneous-Use', ':=', 1)
  insert_into_radius_login(session, 'C', username, 'User-Password', ':=', login_info['pass'])
  if login_info['ip']:
    insert_into_radius_login(session, 'R', username, 'Framed-IP-Address', '==', login_info['ip'])


@supply_mysql_session
def generate_pppoe_login_password(username, session=None):
  sql_query = 'SELECT user FROM login WHERE user = :username;'
  if session.scalar(sql_query, {'username': username}):
    sql_query = 'UPDATE login SET pass = :password WHERE user = :username'
    session.execute(sql_query, {'username': username, 'password': bot_config.default_pppoe_login_password})
    return bot_config.default_pppoe_login_password
  logger.error(msg='generate_pppoe_login_password: user {username} not found'.format(username=username))
  return None


@supply_mysql_session
def get_login_password(username, session=None):
  sql_query = 'SELECT pass FROM login WHERE user = :username;'
  if login_password := session.scalar(sql_query, {'username': username}):
    return login_password.replace('=3F', '?')
  return generate_pppoe_login_password(username, session=session)
