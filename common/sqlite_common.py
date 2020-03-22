from contextlib import contextmanager
from datetime import datetime
from functools import wraps

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import bot_config

Base = declarative_base()


def supply_sqlite_session(function):
  @wraps(function)
  def mysql_session_supplier(*args, **kwargs):
    with sqlite_session() as session:
      return function(session=session, *args, **kwargs)
  return mysql_session_supplier


class OnuDevice(Base):
  __tablename__ = 'onu_devices'
  onu_id = Column(Integer, primary_key=True)
  serial = Column(String)
  username = Column(String)
  last_update = Column(DateTime)

  def __repr__(self):
    return '<OnuDevice=(onu_id={0},serial={1},username={2},last_update={3})>'.format(repr(self.onu_id),
                                                                                     repr(self.serial),
                                                                                     repr(self.username),
                                                                                     str(self.last_update))

  def __init__(self, onu_id, serial=None, username=None):
    self.onu_id = onu_id
    self.serial = serial
    self.username = username
    self.last_update = datetime.now()

  def set_serial(self, serial):
    self.serial = serial
    self.last_update = datetime.now()

  def set_username(self, username):
    self.username = username
    self.last_update = datetime.now()


@contextmanager
def sqlite_session():
  engine = create_engine('sqlite:///{0}'.format(bot_config.sqlite_db_path), encoding='latin1')
  session_maker = sessionmaker(bind=engine)
  session = session_maker()
  try:
    yield session
  finally:
    session.commit()
    session.close()


@supply_sqlite_session
def update_onu_info(onu_id, session=None, serial=None, username=None):
  if not (onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(onu_id)).first()):
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


def print_all_onu_devices(session=None):
  onu_devices = session.query(OnuDevice).all()
  print('List of OnuDevices:')
  for onu_device in onu_devices:
    print(repr(onu_device))
