from datetime import datetime
from re import findall

from requests import post

from common.mysql_common import supply_mysql_session
from common.sqlite_common import supply_sqlite_session, UserLogin, UserLoginChangeAdvertiser
from common.string_common import sanitize_name
from config import bot_config
from logger import get_logger, Log

logger = get_logger('user_login_change_advertiser')


@supply_mysql_session
def get_client_name(username, mysql_session=None):
  query_statement = 'SELECT nome, sexo FROM login INNER JOIN clientes ON cliente_id = clientes.id WHERE user = ' \
                    ':username'
  if client_info := mysql_session.execute(query_statement, {'username': username}).first():
    treatment = 'a' if client_info['sexo'] == 'F' else 'o'
    client_name = sanitize_name(name=client_info['nome'])
    return '{treatment} cliente {client_name}'.format(treatment=treatment, client_name=client_name)
  return None


@supply_sqlite_session
@supply_mysql_session
def update_cached_user_login(username, password, mysql_session=None, sqlite_session=None):
  user_login = sqlite_session.query(UserLogin).filter_by(username=username).first()
  user_login.password = password
  sqlite_session.add(user_login)
  send_advertising_message(username=username, password=password, change='update', mysql_session=mysql_session)
  return True


@supply_mysql_session
def get_live_user_login(username, trial=False, mysql_session=None):
  query_statement = 'SELECT user, pass FROM login WHERE user = :username;'
  if user_login := mysql_session.execute(query_statement, {'username': username}).first():
    return user_login
  if not trial:
    logger.error('get_live_user_login: user not found: {username}'.format(username=username))
  return None


@supply_sqlite_session
def get_cached_user_login(username, trial=False, sqlite_session=None):
  if cached_user_login := sqlite_session.query(UserLogin).filter_by(username=username).first():
    return {'username': cached_user_login.username, 'password': cached_user_login.password}
  if not trial:
    logger.error('get_cached_user_login: user not found: {username}'.format(username=username))
  return None


@supply_sqlite_session
def add_cached_user_login(username, password, mysql_session=None, sqlite_session=None):
  if user_login := sqlite_session.query(UserLogin).filter_by(username=username).first():
    if user_login.password == password:
      return False
    else:
      return update_cached_user_login(username=username, password=user_login['pass'], mysql_session=mysql_session)
  user_login = UserLogin(username=username, password=password)
  sqlite_session.add(user_login)
  send_advertising_message(username=username, password=password, change='add', mysql_session=mysql_session)
  return True


@supply_sqlite_session
@supply_mysql_session
def delete_cached_user_login(username, mysql_session=None, sqlite_session=None):
  if live_user_login := get_live_user_login(username, trial=True, mysql_session=mysql_session):
    if cached_user_login := get_cached_user_login(username, trial=True, sqlite_session=sqlite_session):
      if live_user_login['pass'] != cached_user_login['password']:
        return update_cached_user_login(username=username, password=live_user_login['pass'],
                                        mysql_session=mysql_session, sqlite_session=sqlite_session)
    return add_cached_user_login(username=username, password=live_user_login['pass'],
                                 mysql_session=mysql_session, sqlite_session=sqlite_session)
  if user_login := sqlite_session.query(UserLogin).filter_by(username=username).first():
    sqlite_session.delete(user_login)
    send_advertising_message(username=username, change='delete', mysql_session=mysql_session)
    return True
  logger.error('delete_cached_user_login: user not found: {username}'.format(username=username))
  return False


@Log(logger)
@supply_mysql_session
def send_advertising_message(username, change, password=None, mysql_session=None):
  client_name = get_client_name(username=username, mysql_session=mysql_session) if change != 'delete' else None
  message = {
    'add': '🔹 Novo login criado para {client_name}.\nUsuário: <code>{username}</code>\nSenha: '
           '<code>{password}</code>'.format(client_name=client_name, username=username, password=password),
    'delete': '❌ Login deletado.\nUsuário: <code>{username}</code>'.format(username=username),
    'update': '🔸 Senha de login d{client_name} modificada.\nUsuário: <code>{username}</code>\nNova senha: '
              '<code>{password}</code>'.format(client_name=client_name, username=username, password=password)
  }
  post('https://api.telegram.org/bot{0}/sendMessage'.format(bot_config.token),
       data={'chat_id': bot_config.default_group_chat, 'text': message[change], 'parse_mode': 'HTML'})
  return True


@supply_sqlite_session
def get_last_count(sqlite_session=None):
  if last_count := sqlite_session.query(UserLoginChangeAdvertiser).first():
    return last_count
  new_setup = UserLoginChangeAdvertiser(admlog_count=get_current_count())
  sqlite_session.add(new_setup)
  logger.info('Starting to advertise login changes from now...')
  return new_setup


@supply_sqlite_session
def update_last_count(current_count, last_change, sqlite_session=None):
  last_count_query = sqlite_session.query(UserLoginChangeAdvertiser).first()
  last_count_query.last_count = current_count
  last_count_query.last_change = last_change
  sqlite_session.add(last_count_query)
  return True


@supply_mysql_session
def get_current_count(mysql_session=None):
  query_statement = 'SELECT COUNT(id) FROM admlog;'
  return mysql_session.execute(query_statement).scalar()


@supply_mysql_session
def get_changes(last_change, mysql_session=None):
  clause = "SELECT console, info, timestamp FROM admlog WHERE timestamp > :last_change AND (console = " \
           "'client_login_new' OR console = 'client_login_open_edit' OR console = 'client_login_open_delete') AND " \
           "info LIKE 'Usuário: %' ORDER BY timestamp;"
  return mysql_session.execute(clause=clause, params={'last_change': last_change}).fetchall()


def is_username_defined(info):
  if username := findall('Usuário: ([^\n]*)\n', info):
    return username[0]
  return None


@supply_sqlite_session
@supply_mysql_session
def advertise_changes(mysql_session=None, sqlite_session=None):
  start_time = datetime.now()
  current_count = get_current_count(mysql_session=mysql_session)
  last_count = get_last_count(sqlite_session=sqlite_session)

  if current_count != last_count.admlog_count:
    if changes := get_changes(last_change=last_count.last_change, mysql_session=mysql_session):
      for change in changes:
        if username := is_username_defined(info=change['info']):
          if change['console'] == 'client_login_new':
            if user_login := get_live_user_login(username=username, mysql_session=mysql_session):
              add_cached_user_login(username=user_login['user'], password=user_login['pass'],
                                    mysql_session=mysql_session)
          elif change['console'] == 'client_login_open_delete':
            delete_cached_user_login(username=username, mysql_session=mysql_session)
          elif change['console'] == 'client_login_open_edit':
            if user_login := get_live_user_login(username=username, mysql_session=mysql_session):
              if cached_user_login := get_cached_user_login(username=username, sqlite_session=sqlite_session):
                if user_login['pass'] != cached_user_login['password']:
                  update_cached_user_login(username=username, password=user_login['pass'], mysql_session=mysql_session)
      update_last_count(current_count=current_count, last_change=changes[-1]['timestamp'],
                        sqlite_session=sqlite_session)
  return datetime.now()-start_time


def main():
  logger.debug('ran in {time_elapsed}'.format(time_elapsed=advertise_changes()))
  return 0


if __name__ == '__main__':
  main()
