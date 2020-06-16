from functools import wraps
from socketserver import TCPServer
from threading import Thread

from telnetsrv.threaded import TelnetHandler


class TelnetServer(TCPServer):
  allow_reuse_address = True


def command(method):
  method.alias = []
  method.command_name = method.__name__
  method.hidden = True if method.command_name == 'sudo_password' else False

  @wraps(method)
  def command_wrapper(handler, params):
    params = ' '.join(params)
    print(method.__name__, params)

    if handler.PROMPT == 'Password: ':
      return handler.sudo_auth(params=params, password=method.__name__)

    if method.__name__ not in handler.directories[handler.sudo_enabled][handler.current_directory]:
      handler.writeerror(text='command invalid')
      return handler.ignore_command(params=params)

    return method(self=handler, params=params)
  return command_wrapper


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
    if params or password != 'sudo_password':
      self.PROMPT = 'User> '
      self.writeerror(text='incorrect password\n')
    else:
      self.PROMPT = 'Admin# '
      self.sudo_enabled = True
    return self.ignore_command(params=params)

  def auth_callback(self, username, password):
    if username != self.correct_username or password != self.correct_password:
      raise ConnectionRefusedError

  authCallback = auth_callback

  @command
  def enable(self, params):
    if not params:
      self.PROMPT = 'Password: '
    else:
      self.writeerror(text='invalid params')

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
        self.writeerror(text='this directory is not available with sudo enabled')
      else:
        self.writeerror(text='access denied - enable sudo to access this directory')
    else:
      self.writeerror(text='directory not found')

  @command
  def terminal(self, params):
    if params != 'length 512':
      self.writeerror(text='invalid params')

  @command
  def show(self, params):
    pass

  @command
  def quit(self, params):
    if not params:
      self.cmdEXIT(params=params)
    else:
      self.writeerror(text='invalid params')


class ServerThread(Thread):
  server = TelnetServer(server_address=('localhost', 23), RequestHandlerClass=AN551606BMockHandler)

  def run(self):
    self.server.serve_forever()

  def stop(self):
    self.server.shutdown()


def serve():
  server_thread = ServerThread(daemon=True)
  server_thread.start()
  print('Telnet server started.')
  while True:
    try:
      pass
    except KeyboardInterrupt:
      break
  server_thread.stop()
  print('Telnet server stopped.')


def main():
  serve()


if __name__ == '__main__':
  main()
