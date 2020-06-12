from unittest import TestCase

from tasiap.common.mysql_common import mysql_session_factory, supply_mysql_session, user_exists, insert_into_radius_login, \
  reauthorize_user, generate_pppoe_login_password, get_login_password
from config import bot_config
from tests.mysql_testing_environment import setup_mysql_testing_environment, shutdown_mysql_testing_environment


class TestMySQLFunctions(TestCase):
  sudo_session = None

  @classmethod
  def setUpClass(cls):
    cls.sudo_session = setup_mysql_testing_environment()

  @classmethod
  def tearDownClass(cls):
    shutdown_mysql_testing_environment(sudo_session=cls.sudo_session)

  def tearDown(self):
    self.sudo_session.execute(clause='DELETE FROM login WHERE id > 0;')
    self.sudo_session.execute(clause='DELETE FROM login_radius WHERE id > 0;')
    self.sudo_session.commit()

  def test_mysql_session_factory(self):
    with mysql_session_factory() as session:
      self.assertTrue(expr=session.is_active)

  def test_supply_mysql_session(self):
    @supply_mysql_session
    def generic_mysql_session_dependant_function_a(mysql_session=None):
      return {'repr': repr(mysql_session), 'is_active': mysql_session.is_active}

    @supply_mysql_session
    def generic_mysql_session_dependant_function_b(session=None):
      return {'repr': repr(session), 'is_active': session.is_active}

    with mysql_session_factory() as given_session:
      self.assertEqual(first=repr(given_session),
                       second=generic_mysql_session_dependant_function_a(mysql_session=given_session)['repr'])
      self.assertEqual(first=repr(given_session),
                       second=generic_mysql_session_dependant_function_b(session=given_session)['repr'])

    self.assertTrue(expr=generic_mysql_session_dependant_function_a()['is_active'])
    self.assertTrue(expr=generic_mysql_session_dependant_function_b()['is_active'])

    @supply_mysql_session
    def generic_non_mysql_session_dependant_function(**kwargs):
      return True if 'mysql_session' not in kwargs and 'session' not in kwargs else False

    self.assertTrue(generic_non_mysql_session_dependant_function())

  def test_user_exists(self):
    with mysql_session_factory() as session:
      self.assertFalse(expr=user_exists(user='', session=session))
      self.assertFalse(expr=user_exists(user='username', session=session))

    username_a = 'username_a'
    clause = "INSERT INTO login (user, pass, ip, mac, groupname, proxy) VALUES (:username, '', '', '', '', '');"
    self.sudo_session.execute(clause=clause, params={'username': username_a})
    self.sudo_session.commit()
    with mysql_session_factory() as session:
      self.assertEqual(first=user_exists(user='username_a', session=session), second=username_a)

  def test_insert_into_radius_login(self):
    with mysql_session_factory() as session:
      rtype = 'C'
      username = 'username_a'
      attribute = 'attribute_a'
      op = '=='
      value = 'value_a'
      insert_into_radius_login(rtype=rtype, username=username, attribute=attribute, op=op, value=value,
                               session=session)
      clause = "SELECT type FROM login_radius WHERE type = :type AND user = :username AND op = :op AND " \
               "value = :value AND attribute = :attribute AND enable = 1;"
      params = {'type': rtype, 'username': username, 'op': op, 'value': value, 'attribute': attribute}
      self.assertTrue(expr=session.execute(clause=clause, params=params).first())

  def test_reauthorize_user(self):
    username_a = 'username_a'
    password = 'password_a'
    ip = 'ip_a'
    dirty_attribute = 'dirty_attribute_a'
    dirty_value = 'dirty_value_a'

    clause = "INSERT INTO login (user, pass, ip, mac, groupname, proxy, radsyncframedip, radsyncmac, radsyncsim, " \
             "radsyncmkurl, radnas_id, accesspoint) VALUES (:username, :password, :ip, 'mac_a', '', " \
             "'proxya', 1, 1, 1, 1, 1, 1);"
    self.sudo_session.execute(clause=clause, params={'username': username_a, 'password': password, 'ip': ip})

    insert_into_radius_login(session=self.sudo_session, rtype='C', username=username_a, attribute=dirty_attribute,
                             op='==', value=dirty_value)
    self.sudo_session.commit()

    with mysql_session_factory() as session:
      reauthorize_user(session=session, username=username_a)

    clause = "SELECT COUNT(id) FROM login WHERE user = :username AND pass = :password AND ip = :ip AND mac = '' AND " \
             "groupname = '' AND proxy = 0 AND radsyncframedip = 0 AND radsyncmac = 0 AND radsyncsim = 0 AND " \
             "radnas_id = 0 AND accesspoint = 0;"
    params = {'username': username_a, 'password': password, 'ip': ip}
    self.assertTrue(expr=self.sudo_session.execute(clause=clause, params=params).scalar())

    clause = 'SELECT COUNT(id) FROM login_radius WHERE user = :username AND attribute = :attribute OR value = :value;'
    params = {'username': username_a, 'attribute': dirty_attribute, 'value': dirty_value}
    self.assertFalse(expr=self.sudo_session.execute(clause=clause, params=params).scalar())

    clause = "SELECT COUNT(id) FROM login_radius WHERE type = 'C' AND user = :username AND attribute = " \
             "'Simultaneous-Use' AND op = ':=' AND value = '1' AND enable = 1;"
    self.assertEqual(first=self.sudo_session.execute(clause=clause, params={'username': username_a}).scalar(), second=1)

    clause = "SELECT COUNT(id) FROM login_radius WHERE type = 'C' AND user = :username AND attribute = " \
             "'User-Password' AND op = ':=' AND value = :password AND enable = 1;"
    params = {'username': username_a, 'password': password}
    self.assertEqual(first=self.sudo_session.execute(clause=clause, params=params).scalar(), second=1)

    clause = "SELECT COUNT(id) FROM login_radius WHERE type = 'R' AND user = :username AND attribute = " \
             "'Framed-IP-Address' AND op = '==' AND value = :ip AND enable = 1;"
    params = {'username': username_a, 'ip': ip}
    self.assertEqual(first=self.sudo_session.execute(clause=clause, params=params).scalar(), second=1)

    clause = "SELECT COUNT(id) FROM login_radius WHERE user = :username;"
    self.assertEqual(first=self.sudo_session.execute(clause=clause, params={'username': username_a}).scalar(), second=3)

    username_b = 'username_b'
    clause = "INSERT INTO login (user, pass, ip, mac, groupname, proxy) VALUES (:username, :password, '', '', '', '');"
    self.sudo_session.execute(clause=clause, params={'username': username_b, 'password': password})
    self.sudo_session.commit()

    with mysql_session_factory() as session:
      reauthorize_user(session=session, username=username_b)

    clause = "SELECT COUNT(id) FROM login_radius WHERE user = :username;"
    self.assertEqual(first=self.sudo_session.execute(clause=clause, params={'username': username_b}).scalar(), second=2)

  def test_generate_pppoe_login_password(self):
    username = 'username_a'
    clause = "INSERT INTO login (user, pass, ip, mac, groupname, proxy) VALUES (:username, '', '', '', '', '');"
    self.sudo_session.execute(clause=clause, params={'username': username})
    self.sudo_session.commit()
    self.assertEqual(first=generate_pppoe_login_password(username=username),
                     second=bot_config.default_pppoe_login_password)

    clause = 'SELECT COUNT(id) FROM login WHERE user = :username AND pass = :password;'
    params = {'username': username, 'password': bot_config.default_pppoe_login_password}
    self.assertEqual(first=self.sudo_session.execute(clause=clause, params=params).scalar(), second=1)

    self.assertFalse(expr=generate_pppoe_login_password(username='non_existent_username'))

  def test_get_login_password(self):
    username_a = 'username_a'
    password_a = 'password_a'
    username_b = 'username_b'
    clause = "INSERT INTO login (user, pass, ip, mac, groupname, proxy) VALUES (:username, :password, '', '', '', '');"
    self.sudo_session.execute(clause=clause, params={'username': username_a, 'password': password_a})
    clause = "INSERT INTO login (user, pass, ip, mac, groupname, proxy) VALUES (:username, '', '', '', '', '');"
    self.sudo_session.execute(clause=clause, params={'username': username_b})
    self.sudo_session.commit()
    self.assertEqual(first=get_login_password(username=username_a), second=password_a)
    self.assertEqual(first=get_login_password(username=username_b), second=bot_config.default_pppoe_login_password)
