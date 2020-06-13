from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from config import bot_config
from tasiap.authorize_onu import AuthOnuDevice, Pon, Board
from tasiap.common.sqlite_common import sqlite_session_factory, supply_sqlite_session, get_epoch_timestamp_now, \
  OnuDevice, UserLogin, UserLoginChangeAdvertiser, update_onu_info, find_onu_info
from tasiap.common.string_common import get_auth_onu_device_id


class TestSQLiteFunctions(TestCase):

  @classmethod
  def setUpClass(cls):
    bot_config.sqlite_db_path += '_test'

  @classmethod
  def tearDownClass(cls):
    test_sqlite_database_path = Path(bot_config.sqlite_db_path)
    if test_sqlite_database_path.is_file():
      test_sqlite_database_path.unlink()

  def tearDown(self):
    with sqlite_session_factory() as session:
      session.query(OnuDevice).delete()

  def test_sqlite_session_factory(self):
    with sqlite_session_factory() as session:
      self.assertTrue(expr=session.is_active)

  def test_supply_sqlite_session(self):

    @supply_sqlite_session
    def generic_sqlite_session_dependant_function_a(sqlite_session=None):
      return {'repr': repr(sqlite_session), 'is_active': sqlite_session.is_active}

    @supply_sqlite_session
    def generic_sqlite_session_dependant_function_b(session=None):
      return {'repr': repr(session), 'is_active': session.is_active}

    with sqlite_session_factory() as given_session:
      self.assertEqual(first=repr(given_session),
                       second=generic_sqlite_session_dependant_function_a(sqlite_session=given_session)['repr'])
      self.assertEqual(first=repr(given_session),
                       second=generic_sqlite_session_dependant_function_b(session=given_session)['repr'])

    self.assertTrue(expr=generic_sqlite_session_dependant_function_a()['is_active'])
    self.assertTrue(expr=generic_sqlite_session_dependant_function_b()['is_active'])

    @supply_sqlite_session
    def generic_non_sqlite_session_dependant_function(**kwargs):
      return True if 'sqlite_session' not in kwargs and 'session' not in kwargs else False

    self.assertTrue(generic_non_sqlite_session_dependant_function())

  def test_get_epoch_timestamp_now(self):
    epoch_timestamp_now = int((datetime.now() - datetime.utcfromtimestamp(0)).total_seconds())
    self.assertEqual(first=get_epoch_timestamp_now(), second=epoch_timestamp_now)

  def test_update_onu_info(self):
    serial_a = 'FHTT1177bc38'
    board_id_a = '14'
    pon_id_a = '1'
    onu_number_a = 4
    username_a = 'username_a'
    board_a = Board(board_id_a)

    onu_id_b = 1206
    username_b = 'username_b'

    def mock_init_pon(pon, pon_id, board):
      pon.pon_id = pon_id
      pon.board = board

    with patch.object(Pon, '__init__', mock_init_pon):
      pon_a = Pon(pon_id=pon_id_a, board=board_a)
      onu_a = AuthOnuDevice(authorization_id='1', onu_type='AN5506-04-F1', phy_id=serial_a, pon=pon_a)
      onu_a.number = onu_number_a
      onu_id_a = int(get_auth_onu_device_id(onu_device=onu_a))
      update_onu_info(auth_onu_device=onu_a)

    with sqlite_session_factory() as session:
      self.assertTrue(expr=session.query(OnuDevice).filter_by(onu_id=onu_id_a, serial=serial_a).first())

    update_onu_info(auth_onu_device=onu_a)
    with sqlite_session_factory() as session:
      self.assertTrue(expr=session.query(OnuDevice).filter_by(onu_id=onu_id_a, serial=serial_a).first())

    update_onu_info(auth_onu_device=onu_a, username=username_a)
    with sqlite_session_factory() as session:
      self.assertTrue(expr=session.query(OnuDevice).filter_by(onu_id=onu_id_a, serial=serial_a,
                                                              username=username_a).first())

    update_onu_info(onu_id=onu_id_b)
    with sqlite_session_factory() as session:
      self.assertTrue(expr=session.query(OnuDevice).filter_by(onu_id=onu_id_b).first())

    update_onu_info(onu_id=onu_id_b, username=username_b)
    with sqlite_session_factory() as session:
      self.assertTrue(expr=session.query(OnuDevice).filter_by(onu_id=onu_id_b, username=username_b).first())

  def test_find_onu_info(self):
    onu_id = 1234
    username = 'username'
    serial = 'serial'

    self.assertFalse(expr=find_onu_info())
    self.assertFalse(expr=find_onu_info(onu_id='1234'))
    self.assertFalse(expr=find_onu_info(serial='serial'))
    self.assertFalse(expr=find_onu_info(username='username'))

    update_onu_info(onu_id=onu_id, username=username, serial=serial)
    found_onu_info_a = find_onu_info(onu_id=onu_id)
    self.assertEqual(first=found_onu_info_a['onu_id'], second=onu_id)
    self.assertEqual(first=found_onu_info_a['username'], second=username)
    self.assertEqual(first=found_onu_info_a['serial'], second=serial)

    found_onu_info_b = find_onu_info(serial=serial)
    self.assertEqual(first=found_onu_info_b['onu_id'], second=onu_id)
    self.assertEqual(first=found_onu_info_b['username'], second=username)
    self.assertEqual(first=found_onu_info_b['serial'], second=serial)

    found_onu_info_c = find_onu_info(username=username)
    self.assertEqual(first=found_onu_info_c['onu_id'], second=onu_id)
    self.assertEqual(first=found_onu_info_c['username'], second=username)
    self.assertEqual(first=found_onu_info_c['serial'], second=serial)


class TestOnuDevice(TestCase):

  def setUp(self):
    self.onu_id_a = '1234'
    self.datetime_before = datetime.now()
    self.onu_device_a = OnuDevice(onu_id=self.onu_id_a)
    self.datetime_after = datetime.now()

  def test_init(self):

    self.assertEqual(first=self.onu_device_a.onu_id, second=int(self.onu_id_a))
    self.assertFalse(expr=self.onu_device_a.serial)
    self.assertFalse(expr=self.onu_device_a.username)

    self.assertTrue(expr=self.datetime_before <= self.onu_device_a.last_update <= self.datetime_after)

    onu_id_b = '3210'
    serial_b = 'b1'
    username_b = 'b1'
    onu_device_b = OnuDevice(onu_id=onu_id_b, serial=serial_b, username=username_b)
    self.assertEqual(first=onu_device_b.serial, second=serial_b)
    self.assertEqual(first=onu_device_b.username, second=username_b)

  def test_set_serial(self):
    serial = 'a0'
    datetime_before = datetime.now()
    self.onu_device_a.set_serial(serial=serial)
    datetime_after = datetime.now()
    self.assertEqual(first=self.onu_device_a.serial, second=serial)
    self.assertTrue(expr=datetime_before <= self.onu_device_a.last_update <= datetime_after)

  def test_set_username(self):
    username = 'a0'
    datetime_before = datetime.now()
    self.onu_device_a.set_username(username=username)
    datetime_after = datetime.now()
    self.assertEqual(first=self.onu_device_a.username, second=username)

    self.assertTrue(expr=datetime_before <= self.onu_device_a.last_update <= datetime_after)

  def test_repr(self):
    self.onu_device_a.last_update = datetime(2020, 6, 12, 13, 17, 0, 338460)
    self.assertEqual(first=repr(self.onu_device_a),
                     second='<OnuDevice=(onu_id=1234,serial=None,username=None,last_update=datetime.datetime(2020, 6, '
                            '12, 13, 17, 0, 338460))>')


class TestUserLogin(TestCase):

  def setUp(self):
    self.username_a = 'a6'
    self.user_login_a = UserLogin(username=self.username_a)

  def test_init(self):
    self.assertEqual(first=self.user_login_a.username, second=self.username_a)
    self.assertFalse(expr=self.user_login_a.password)
    username_b = 'b6'
    password_b = '6b'
    user_login_b = UserLogin(username=username_b, password=password_b)
    self.assertEqual(first=user_login_b.username, second=username_b)
    self.assertEqual(first=user_login_b.password, second=password_b)

  def test_repr(self):
    self.assertEqual(first=repr(self.user_login_a), second="<UserLogin(username='a6',password=None)>")


class TestUserLoginChangeAdvertiser(TestCase):

  def setUp(self):
    self.admlog_count = 6
    self.epoch_timestamp_now = get_epoch_timestamp_now()
    self.user_login_change_advertiser = UserLoginChangeAdvertiser(admlog_count=self.admlog_count)

  def test_init(self):
    self.assertEqual(first=self.user_login_change_advertiser.admlog_count, second=self.admlog_count)
    self.assertEqual(first=self.user_login_change_advertiser.last_change, second=self.epoch_timestamp_now)

  def test_repr(self):
    self.user_login_change_advertiser.last_change = 1591969503
    self.assertEqual(first=repr(self.user_login_change_advertiser),
                     second='<UserLoginChangeAdvertiser(admlog_count=6,last_check=1591969503)>')
