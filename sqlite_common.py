#!/usr/bin/env python3.8
# coding=utf-8

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import logging
import bot_config

logger = logging.getLogger('sqlite_common')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/sqlite_common.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

Base = declarative_base()

class OnuDevice(Base):
  __tablename__ = 'onu_devices'
  onu_id = Column(Integer, primary_key=True)
  serial = Column(String)
  username = Column(String)
  last_update = Column(DateTime)
  def __repr__(self):
    return '<OnuDevice=(onu_id={0},serial={1},username={2},last_update={3})>'.format(repr(self.onu_id), repr(self.serial), repr(self.username), str(self.last_update))
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
  Session = sessionmaker(bind=engine)
  return Session()

def update_onu_info(session, onu_id, serial=None, username=None):
  if not (onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(onu_id)).first()):
    onu_device = OnuDevice(onu_id, serial=serial, username=username)
  else:
    if serial:
      onu_device.set_serial(serial)
    if username:
      onu_device.set_username(username)
  session.add(onu_device)
  session.commit()

def find_onu_info(session, onu_id=None, serial=None, username=None):
  onu_info = {'found': False, 'onu_id': None, 'serial': None, 'username': None, 'last_update': None}
  if onu_id:
    if (onu_device := session.query(OnuDevice).filter(OnuDevice.onu_id.is_(onu_id)).first()):
      onu_info['found'] = True
      onu_info['onu_id'] = onu_id
      onu_info['serial'] = onu_device.serial
      onu_info['username'] = onu_device.username
      onu_info['last_update'] = str(onu_device.last_update)
  elif serial:
    if (onu_device := session.query(OnuDevice).filter(OnuDevice.serial.is_(serial)).first()):
      onu_info['found'] = True
      onu_info['onu_id'] = onu_device.onu_id
      onu_info['serial'] = serial
      onu_info['username'] = onu_device.username
      onu_info['last_update'] = str(onu_device.last_update)
  elif username:
    if (onu_device := session.query(OnuDevice).filter(OnuDevice.username.is_(username)).first()):
      onu_info['found'] = True
      onu_info['onu_id'] = onu_device.onu_id
      onu_info['serial'] = onu_device.serial
      onu_info['username'] = username
      onu_info['last_update'] = str(onu_device.last_update)
  return onu_info

def print_all_onu_devices(session):
  onu_devices = session.query(OnuDevice).all()
  print('List of OnuDevices:')
  for onu_device in onu_devices:
    print(repr(onu_device))

def main():
  logger.info('Executing main function...')

  session = get_sqlite_session()
  logger.info('SQLite session created.')

  update_onu_info(session, 1324, username='saugusto')
  logger.info('OnuDevice created.')

  logger.info('find_onu_info: username: saugusto\n{0}'.format(find_onu_info(session, username='saugusto')))
  logger.info('find_onu_info: onu_id: 1324\n{0}'.format(find_onu_info(session, onu_id=1324)))

  print_all_onu_devices(session)

  session.close()
  logger.info('Done.')

  return 0

if __name__ == '__main__':
  main()