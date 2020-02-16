#!/usr/bin/env python3.8
# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mysqldb_config

def get_mysql_session():
  engine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(mysqldb_config.username, mysqldb_config.password, mysqldb_config.host, mysqldb_config.database), encoding='latin1')
  Session = sessionmaker(bind=engine)
  return Session()

def user_exists(session, user):
  return session.execute('SELECT user FROM login WHERE user = :user;', {'user': user}).scalar()