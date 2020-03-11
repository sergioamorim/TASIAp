from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.string_common import is_int
from config import mysqldb_config


def get_mysql_session():
  engine = create_engine(
    'mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host,
                                     mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  return Session()


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
