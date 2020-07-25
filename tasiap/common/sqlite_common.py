from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from inspect import signature

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import bot_config
from tasiap.common.string_common import get_auth_onu_device_id

Base = declarative_base()


def supply_sqlite_session(function):
  @wraps(function)
  def sqlite_session_supplier(*args, **kwargs):
    available_args = signature(function).parameters.keys()
    if 'sqlite_session' in available_args:
      if 'sqlite_session' not in kwargs:
        with sqlite_session_factory() as sqlite_session:
          return function(sqlite_session=sqlite_session, *args, **kwargs)
    elif 'session' in available_args:
      if 'session' not in kwargs:
        with sqlite_session_factory() as sqlite_session:
          return function(session=sqlite_session, *args, **kwargs)
    return function(*args, **kwargs)
  return sqlite_session_supplier


class OnuDevice(Base):
  __tablename__ = 'onu_devices'
  onu_id = Column(Integer, primary_key=True)
  serial = Column(String)
  username = Column(String)
  last_update = Column(DateTime)

  def __repr__(self):
    return '<OnuDevice=(onu_id={0!r},serial={1!r},username={2!r},last_update={3!r})>'.format(self.onu_id, self.serial,
                                                                                             self.username,
                                                                                             self.last_update)

  def __init__(self, onu_id, serial=None, username=None):
    self.onu_id = int(onu_id)
    self.serial = serial
    self.username = username
    self.last_update = datetime.now()

  def set_serial(self, serial):
    self.serial = serial
    self.last_update = datetime.now()

  def set_username(self, username):
    self.username = username
    self.last_update = datetime.now()


class UserLogin(Base):
  __tablename__ = 'user_login'
  username = Column(String, primary_key=True)
  password = Column(String)

  def __init__(self, username, password=None):
    self.username = username
    self.password = password

  def __repr__(self):
    return '<UserLogin(username={username!r},password={password!r})>'.format(
            username=self.username, password=self.password)


class UserLoginChangeAdvertiser(Base):
  __tablename__ = 'user_login_change_advertiser'
  admlog_count = Column(Integer, primary_key=True)
  last_change = Column(Integer, primary_key=True)

  def __init__(self, admlog_count):
    self.admlog_count = admlog_count
    self.last_change = get_epoch_timestamp_now()

  def __repr__(self):
    return '<UserLoginChangeAdvertiser(admlog_count={admlog_count!r},last_check={last_change!r})>'.format(
            admlog_count=self.admlog_count, last_change=self.last_change)


def get_epoch_timestamp_now():
  return int((datetime.now() - datetime.utcfromtimestamp(0)).total_seconds())


@contextmanager
def sqlite_session_factory():
  engine = create_engine('sqlite:///{0}'.format(bot_config.sqlite_db_path), encoding='latin1')
  Base.metadata.create_all(bind=engine)
  session_maker = sessionmaker(bind=engine)
  session = session_maker()
  try:
    yield session
  finally:
    session.commit()
    session.close()


@supply_sqlite_session
def update_onu_info(auth_onu_device=None, onu_id=None, session=None, serial=None, username=None):
  if auth_onu_device:
    onu_id = get_auth_onu_device_id(auth_onu_device)
    serial = auth_onu_device.phy_id
  if not (onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(int(onu_id))).first()):
    onu_device = OnuDevice(onu_id, serial=serial, username=username)
  else:
    if serial:
      onu_device.set_serial(serial)
    if username:
      onu_device.set_username(username)
  session.add(onu_device)


@supply_sqlite_session
def find_onu_info(session=None, onu_id=None, serial=None, username=None):
  if onu_id:
    if onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(onu_id)).first():
      return {'onu_id': onu_id, 'serial': onu_device.serial, 'username': onu_device.username,
              'last_update': onu_device.last_update}
  elif serial:
    if onu_device := session.query(OnuDevice).filter(OnuDevice.serial.is_(serial)).order_by(OnuDevice.last_update.desc()
                                                                                            ).first():
      return {'onu_id': onu_device.onu_id, 'serial': serial, 'username': onu_device.username,
              'last_update': onu_device.last_update}
  elif username:
    if (onu_device := session.query(OnuDevice).filter(OnuDevice.username.is_(username)).order_by(
          OnuDevice.last_update.desc()).first()):
      return {'onu_id': onu_device.onu_id, 'serial': onu_device.serial, 'username': username,
              'last_update': onu_device.last_update}
  return None
