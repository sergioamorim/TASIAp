import unittest
from os import unlink
from os.path import abspath
from shutil import copyfile
from subprocess import run

from config import telnet_config
from config.telnet_config import password_sudo
from config.testing_config import python_binary_path
from tasiap import onu_signal_power
from tasiap.onu_signal_power import get_signal_power, get_onu_power_signal_by_id
from tests.data.telnet_testing_data import test_params, test_data
from tests.telnet_testing_environment import TelnetTestingEnvironment


def translate_onu_id(board_id, pon_id, onu_number):
  board_reference = '1' if board_id == '12' else '2'
  onu_reference = '0{onu_number}'.format(
    onu_number=onu_number
  ) if int(onu_number) < 10 else onu_number

  return '{board_reference}{pon_id}{onu_reference}'.format(
    board_reference=board_reference,
    pon_id=pon_id,
    onu_reference=onu_reference
  )


class TestOutputMethods(unittest.TestCase):

  telnet_testing_environment = None

  @classmethod
  def setUpClass(cls):
    cls.original_sudo_password = password_sudo
    cls.telnet_port = 23236
    cls.telnet_username = 'a'
    cls.telnet_password = 'b'

    cls.telnet_testing_environment = TelnetTestingEnvironment(
      port=cls.telnet_port,
      username=cls.telnet_username,
      password=cls.telnet_password
    )

    cls.telnet_testing_environment.setup()

  @classmethod
  def tearDownClass(cls):
    cls.telnet_testing_environment.tear_down()

  def test_get_signal_power(self):
    for test in test_params.keys():
      data = get_signal_power(show_optic_module=test_data[test]['optic_module'])
      self.assertEqual(first=test_params[test]['signal_power'], second=data)

  def test_get_onu_power_signal_by_id(self):

      for test in test_params.keys():

        onu_id = translate_onu_id(
          board_id=test_params[test]['board_id'],
          pon_id=test_params[test]['pon_id'],
          onu_number=test_params[test]['onu_number']
        )

        data = get_onu_power_signal_by_id(onu_id=onu_id)

        self.assertEqual(first=test_params[test]['signal_power'], second=data)

  def test_command_line_execution(self):
    original_config_path = abspath(telnet_config.__file__)

    copyfile(
      original_config_path,
      '{original_config_path}_backup'.format(original_config_path=original_config_path)
    )

    unlink(original_config_path)

    with open(original_config_path, mode='w') as telnet_config_file:
      print("ip = 'localhost'", file=telnet_config_file)

      print(
        'port = {port}'.format(port=self.telnet_port),
        file=telnet_config_file
      )

      print(
        "username = '{username}'".format(username=self.telnet_username),
        file=telnet_config_file
      )

      print(
        "password = '{password}'".format(password=self.telnet_password),
        file=telnet_config_file
      )

      print(
        "password_sudo = '{sudo_password}'".format(sudo_password=self.original_sudo_password),
        file=telnet_config_file
      )

    try:
      for test in test_params.keys():

        onu_id = translate_onu_id(
          board_id=test_params[test]['board_id'],
          pon_id=test_params[test]['pon_id'],
          onu_number=test_params[test]['onu_number']
        )

        data = run('{python_binary_path} {onu_signal_power} -i {onu_id}'.format(
          python_binary_path=python_binary_path,
          onu_signal_power=abspath(onu_signal_power.__file__),
          onu_id=onu_id
        ), capture_output=True).stdout.decode('ascii').replace('\r\n', '')

        self.assertEqual(first=test_params[test]['signal_power'], second=data)
    finally:
      try:
        unlink(original_config_path)

        copyfile(
          '{original_config_path}_backup'.format(original_config_path=original_config_path),
          original_config_path
        )

      finally:
        unlink('{original_config_path}_backup'.format(original_config_path=original_config_path))
