from functools import wraps
from re import findall
from socketserver import TCPServer
from threading import Thread

from telnetsrv.threaded import TelnetHandler

from config import telnet_config
from tests.data.telnet_testing_data import test_params, test_data


class TelnetServer(TCPServer):
  allow_reuse_address = True


def command(method):
  method.alias = []
  method.command_name = telnet_config.password_sudo if method.__name__ == 'sudo_password' else method.__name__
  method.hidden = True if method.command_name == telnet_config.password_sudo else False

  @wraps(method)
  def command_wrapper(handler, params):
    params = ' '.join(params)

    if handler.PROMPT == 'Password: ':
      return handler.sudo_auth(params=params, password=method.command_name)

    if method.command_name not in handler.directories[handler.sudo_enabled][handler.current_directory]:
      handler.writeerror(text="Unknown command '{command_name}'\n".format(command_name=method.command_name.upper()))
      return handler.ignore_command(params=params)

    return method(self=handler, params=params)
  return command_wrapper


class AN551606BMockHandler(TelnetHandler):
  PROMPT = 'User> '
  WELCOME = ''
  authNeedUser = True
  authNeedPass = True
  sudo_enabled = False
  current_directory = 'root'
  paths = {
    True: {
      '': 'root',
      '..': 'root',
      'service': 'service',
      'gpononu': 'gpononu'
    },
    False: {
      '': 'root',
      '..': 'root'
    }
  }
  directories = {
    True: {
      'root': ['cd', 'quit'],
      'service': ['cd', 'quit', 'terminal'],
      'gpononu': ['cd', 'quit', 'show'],
    },
    False: {
      'root': ['cd', 'quit', 'enable']
    }
  }

  def ignore_command(self, params):
    pass

  def sudo_auth(self, params, password):
    if params or password != telnet_config.password_sudo:
      self.PROMPT = 'User> '
      self.writeerror(text='incorrect password\n')
    else:
      self.PROMPT = 'Admin# '
      self.sudo_enabled = True
    return self.ignore_command(params=params)

  def auth_callback(self, username, password):
    if username != telnet_config.username or password != telnet_config.password:
      self.writeerror('invalid username or password\n')
      raise ConnectionRefusedError

  authCallback = auth_callback

  @command
  def enable(self, params):
    if not params:
      self.PROMPT = 'Password: '
    else:
      self.writeerror(text='invalid params\n')

  @command
  def sudo_password(self, params):
    pass

  @command
  def cd(self, params):

    if params in self.paths[self.sudo_enabled]:
      self.current_directory = self.paths[self.sudo_enabled][params]
      self.PROMPT = make_prompt(prompt=self.PROMPT, path=self.current_directory)
    elif params in self.paths[not self.sudo_enabled]:
      if self.sudo_enabled:
        self.writeerror(text='this directory is not available with sudo enabled\n')
      else:
        self.writeerror(text='access denied - enable sudo to access this directory\n')
    else:
      self.writeerror(text='directory not found\n')

  @command
  def terminal(self, params):
    if params != 'length 512':
      self.writeerror(text='invalid params\n')

  def show_process_test(self, sub_command, board_id, pon_id, onu_number):
    text = None
    for test in test_params.keys():
      if are_params_from_test(
          board_id=board_id,
          pon_id=pon_id,
          onu_number=onu_number,
          test=test
      ):
        text = test_data[test][sub_command][2:].replace('\r', '')
    self.writeresponse(text=text or test_data['default'][sub_command][2:].replace('\r', ''))

  @command
  def show(self, params):
    link_address_pattern = 'slot (12|14) link ([1-8])'

    sub_command_onu_address_pattern = '(wifi_serv|optic_module) {link_address_pattern} onu ([1-9][0-9]?)'.format(
      link_address_pattern=link_address_pattern
    )

    sub_command_link_address_pattern = 'authorization {link_address_pattern}'.format(
      link_address_pattern=link_address_pattern
    )

    if onu_params := findall(string=params, pattern=sub_command_onu_address_pattern):
      sub_command = onu_params[0][0]
      board_id = onu_params[0][1]
      pon_id = onu_params[0][2]
      onu_number = onu_params[0][3]

      self.show_process_test(
        sub_command=sub_command,
        board_id=board_id,
        pon_id=pon_id,
        onu_number=onu_number,
      )

    elif findall(string=params, pattern=sub_command_link_address_pattern):
      self.writeresponse(test_data['default']['authorization'])
    elif params == 'discovery slot all link all':
      self.writeresponse(test_data['default']['discovery'])
    else:
      self.writeerror(text='invalid_params\n')

  @command
  def quit(self, params):
    if not params:
      self.cmdEXIT(params=params)
    else:
      self.writeerror(text='invalid params\n')


class ServerThread(Thread):
  def __init__(self):
    self.server = TelnetServer(server_address=('localhost', telnet_config.port),
                               RequestHandlerClass=AN551606BMockHandler)
    super().__init__(daemon=True)

  def run(self):
    self.server.serve_forever()

  def stop(self):
    self.server.shutdown()


def make_prompt(prompt, path):
  user = 'Admin' if 'Admin' in prompt else 'User'
  division = '\\' if path != 'root' else ''
  path = '' if path == 'root' else path
  command_symbol = '#' if user == 'Admin' else '>'
  return '{user}{division}{path}{command_symbol} '.format(
    user=user,
    division=division,
    path=path,
    command_symbol=command_symbol
  )


def are_params_from_test(board_id, pon_id, onu_number, test):
  return (
      test in test_params and
      test_params[test]['board_id'] == board_id and
      test_params[test]['pon_id'] == pon_id and
      test_params[test]['onu_number'] == onu_number
  )


def serve():
  server_thread = ServerThread()
  server_thread.start()
  print('Telnet server started.')
  while True:
    try:
      pass
    except KeyboardInterrupt:
      break
  server_thread.stop()
  print('Telnet server stopped.')


class TelnetTestingEnvironment:
  server_thread = None

  def __init__(self, port, username='a', password='b'):
    self.username = username
    self.password = password
    self.port = port

  def setup(self):
    # the telnet_config.password_sudo is processed before runtime, at the AN551606BMockHandler class definition,
    # so the real password_sudo is used here. make sure to change telnet_config.username, telnet_config.password and
    # telnet_config.port to prevent mistakes; also, change the telnet_config.ip to localhost
    telnet_config.username = self.username
    telnet_config.password = self.password
    telnet_config.ip = 'localhost'  # hardcoded in the ServerThread constructor from telnet_testing_environment
    telnet_config.port = self.port
    self.server_thread = ServerThread()
    self.server_thread.start()

  def tear_down(self):
    self.server_thread.stop()


def main():
  serve()


if __name__ == '__main__':
  main()
