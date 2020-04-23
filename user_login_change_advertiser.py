from datetime import datetime

from requests import post

from common.mysql_common import supply_mysql_session
from common.sqlite_common import supply_sqlite_session, UserLogin
from common.string_common import sanitize_name
from config import mysqldb_config, bot_config
from logger import get_logger, Log

logger = get_logger('user_login_change_advertiser')


class UserLoginInfo:

  def __init__(self, username, password):
    self.username = username
    self.password = password

  def __repr__(self):
    return '<UserLoginInfo(username={username!r},password={password!r})>'.format(
            username=self.username, password=self.password)

  def __hash__(self):
    return hash(self.username)

  def __eq__(self, other):
    return self.username == other.username and self.password == other.password

  def __lt__(self, other):
    return self.username < other.username


@supply_mysql_session
def get_live_info_set(session=None):
  query_results = session.execute('SELECT user, pass FROM {login_table}'.format(login_table=mysqldb_config.login_table))
  return set(UserLoginInfo(username=result['user'], password=result['pass']) for result in query_results)


@supply_sqlite_session
def get_cached_info_set(session=None):
  user_logins = session.query(UserLogin)
  return set(UserLoginInfo(username=user_login.username, password=user_login.password) for user_login in user_logins)


@supply_mysql_session
def get_client_name(username, session=None):
  return session.scalar('SELECT nome FROM {login_table} INNER JOIN {clientes_table} ON cliente_id = '
                        'clientes.id WHERE user = :username'.format(login_table=mysqldb_config.login_table,
                                                                    clientes_table=mysqldb_config.clientes_table), {
                                                                    'username': username})


@supply_sqlite_session
def update_cached_user_login(username, password, mysql_session, session=None):
  user_login = session.query(UserLogin).filter_by(username=username).first()
  user_login.password = password
  session.add(user_login)
  send_advertising_message(username=username, password=password, change='update', session=mysql_session)
  return True


@supply_sqlite_session
def add_cached_user_login(username, password, mysql_session, session=None):
  user_login = UserLogin(username=username, password=password)
  session.add(user_login)
  send_advertising_message(username=username, password=password, change='add', session=mysql_session)
  return True


@supply_sqlite_session
def delete_cached_user_login(username, mysql_session, session=None):
  user_login = session.query(UserLogin).filter_by(username=username).first()
  session.delete(user_login)
  send_advertising_message(username=username, change='delete', session=mysql_session)
  return True


@Log(logger)
@supply_mysql_session
def send_advertising_message(username, change, password=None, session=None):
  client_name = sanitize_name(name=get_client_name(username=username, session=session)) if change != 'delete' else None
  message = {
    'add': '🔹 Novo login criado para o cliente {client_name}.\nUsuário: <code>{username}</code>\nSenha: '
           '<code>{password}</code>'.format(client_name=client_name, username=username, password=password),
    'delete': '❌ Login deletado.\nUsuário: <code>{username}</code>'.format(username=username),
    'update': '🔸 Senha de login do cliente {client_name} modificada.\nUsuário: <code>{username}</code>\nNova senha: '
              '<code>{password}</code>'.format(client_name=client_name, username=username, password=password)
  }
  post('https://api.telegram.org/bot{0}/sendMessage'.format(bot_config.token),
       data={'chat_id': bot_config.default_group_chat, 'text': message[change], 'parse_mode': 'HTML'})
  return True


def find_user_info_in_set(username, user_info_set):
  for user_info in user_info_set:
    if user_info.username == username:
      return user_info
  return None


@supply_mysql_session
def advertise_changes(session=None):
  start_time = datetime.now()
  cached_info_set = get_cached_info_set()
  live_info_set = get_live_info_set()

  if changes := cached_info_set.symmetric_difference(live_info_set):
    updated_usernames = set()
    for user_info in changes:
      if cached_user_info := find_user_info_in_set(username=user_info.username, user_info_set=cached_info_set):
        if live_user_info := find_user_info_in_set(username=user_info.username, user_info_set=live_info_set):
          if cached_user_info.password != live_user_info.password and user_info.username not in updated_usernames:
            update_cached_user_login(username=user_info.username, password=live_user_info.password,
                                     mysql_session=session)
            updated_usernames.add(user_info.username)
        else:
          delete_cached_user_login(username=user_info.username, mysql_session=session)
      else:
        add_cached_user_login(username=user_info.username, password=user_info.password, mysql_session=session)
  return datetime.now()-start_time


def main():
  logger.debug('ran in {time_elapsed}'.format(time_elapsed=advertise_changes()))
  return 0


if __name__ == '__main__':
  main()
