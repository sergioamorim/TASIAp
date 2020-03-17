from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import bot_config

Base = declarative_base()


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


def get_sqlite_session():
  engine = create_engine('sqlite:///{0}'.format(bot_config.sqlite_db_path), encoding='latin1')
  Base.metadata.create_all(engine)
  session_maker = sessionmaker(bind=engine)
  return session_maker()


def update_onu_info(onu_id, serial=None, username=None):
  session = get_sqlite_session()
  if not (onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(onu_id)).first()):
    onu_device = OnuDevice(onu_id, serial=serial, username=username)
  else:
    if serial:
      onu_device.set_serial(serial)
    if username:
      onu_device.set_username(username)
  session.add(onu_device)
  session.commit()
  session.close()


def find_onu_info(onu_id=None, serial=None, username=None):
  session = get_sqlite_session()
  if onu_id:
    if onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(onu_id)).first():
      session.close()
      return {'onu_id': onu_id, 'serial': onu_device.serial, 'username': onu_device.username,
              'last_update': onu_device.last_update}
  elif serial:
    if onu_device := session.query(OnuDevice).filter(OnuDevice.serial.is_(serial)).order_by(OnuDevice.last_update.desc()
                                                                                            ).first():
      session.close()
      return {'onu_id': onu_device.onu_id, 'serial': serial, 'username': onu_device.username,
              'last_update': onu_device.last_update}
  elif username:
    if (onu_device := session.query(OnuDevice).filter(OnuDevice.username.is_(username)).order_by(
          OnuDevice.last_update.desc()).first()):
      session.close()
      return {'onu_id': onu_device.onu_id, 'serial': onu_device.serial, 'username': username,
              'last_update': onu_device.last_update}
  session.close()
  return None


def print_all_onu_devices():
  session = get_sqlite_session()
  onu_devices = session.query(OnuDevice).all()
  session.close()
  print('List of OnuDevices:')
  for onu_device in onu_devices:
    print(repr(onu_device))
