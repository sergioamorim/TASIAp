from functools import wraps
from socketserver import TCPServer
from threading import Thread

from telnetsrv.threaded import TelnetHandler, command


class TelnetServer(TCPServer):
  allow_reuse_address = True


def check_environment(method):
  @wraps(method)
  def check_environment_wraper(handler, params, *args, **kwargs):
    params = ' '.join(params)
    print(method.__name__, params)

    if handler.PROMPT == 'Password: ':
      return handler.sudo_auth(params=params, password=method.__name__)

    if not is_command_valid(handler=handler, command_requested=method.__name__, params=params):
      handler.writeerror(text='wrong input\n')
      return handler.ignore_command(params)

    return method(self=handler, params=params, *args, **kwargs)
  return check_environment_wraper


def is_command_valid(handler, command_requested, params):
  return (
      command_requested in handler.directories[handler.sudo_enabled][handler.current_directory] and
      params in handler.directories[handler.sudo_enabled][handler.current_directory][command_requested]
  )


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


class AN551606BMockHandler(TelnetHandler):
  PROMPT = 'User> '
  WELCOME = ''
  authNeedUser = True
  authNeedPass = True
  correct_username = 'a'
  correct_password = 'b'
  sudo_enabled = False
  current_directory = 'root'
  sudo_cd_params = {
    '': 'root',
    'service': 'service',
    'gpononu': 'gpononu'
  }
  directories = {
    True: {
      'root': {
        'cd': sudo_cd_params,
      },
      'service': {
        'cd': sudo_cd_params,
        'terminal': ['length 512'],
      },
      'gpononu': {
        'cd': sudo_cd_params,
        'show': [''],
      },
    },
    False: {
      'root': {
        'cd': {'': 'root'},
        'enable': [''],
      }
    },
  }

  def ignore_command(self, params):
    pass

  def sudo_auth(self, params, password):
    if password != 'sudo_password':
      self.PROMPT = 'User> '
      self.writeerror(text='incorrect password\n')
    else:
      self.PROMPT = 'Admin# '
      self.sudo_enabled = True
    return self.ignore_command(params)

  def auth_callback(self, username, password):
    if username != self.correct_username or password != self.correct_password:
      raise ConnectionRefusedError

  authCallback = auth_callback

  @command(names=['en', 'enable'])
  @check_environment
  def enable(self, params):
    self.PROMPT = 'Password: '

  @command(names='sudo_password', hidden=True)
  @check_environment
  def sudo_password(self, params):
    pass

  @command(names='cd')
  @check_environment
  def cd(self, params):
    self.current_directory = self.sudo_cd_params[params]
    self.PROMPT = make_prompt(prompt=self.PROMPT, path=self.current_directory)

  @command(names='terminal')
  @check_environment
  def terminal(self, params):
    pass


class ServerThread(Thread):
  server = TelnetServer(server_address=('localhost', 23), RequestHandlerClass=AN551606BMockHandler)

  def run(self):
    self.server.serve_forever()

  def stop(self):
    self.server.shutdown()
    print('Telnet server stopped.')


def serve():
  server_thread = ServerThread(daemon=True)
  server_thread.start()
  print('Telnet server started.')
  while input() != 'exit':
    continue
  server_thread.stop()


def main():
  serve()


if __name__ == '__main__':
  main()
