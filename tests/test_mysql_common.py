from subprocess import run
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from common.mysql_common import mysql_session_factory
from config import mysqldb_config


class TestMySQLFunctions(TestCase):
  sudo_session = None
  sudo_username = 'sergio'
  sudo_password = 'paloma'
  sudo_engine_parameters = 'mysql://{username}:{password}@{host}:{port}/{database}'.format(
    username=sudo_username, password=sudo_password, host=mysqldb_config.host, port=mysqldb_config.port,
    database=mysqldb_config.database)

  @classmethod
  def setUpClass(cls):
    command = 'mysql -h {host} -u {username} -p{password} < data/test_mysql_myauth_admin_database_structure.sql'.format(
      host=mysqldb_config.host, username=cls.sudo_username, password=cls.sudo_password)
    run(args=command, shell=True, check=True)

    engine = create_engine(cls.sudo_engine_parameters, encoding='latin1')
    session_maker = sessionmaker(bind=engine)
    cls.sudo_session = session_maker()

  @classmethod
  def tearDownClass(cls):
    cls.sudo_session.execute('DROP DATABASE IF EXISTS test_admin;')
    cls.sudo_session.commit()
    cls.sudo_session.close()

  def test_mysql_session_factory(self):
    with mysql_session_factory() as session:
      self.assertTrue(session.is_active)
