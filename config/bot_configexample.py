# The config file needs to be named 'bot_config.py'

token = 'bOt-T0keN_ExaMplE'
default_chat = '12345678'
default_group_chat = '-123456789012'
default_pppoe_login_password = 'defaultpass'
default_web_config_password = 'defaultwebpass'
permissions = {
  'autorizar': [1234567, 89012345],
  'authorize': [1234567],
  'sinal': [1234567],
  'reiniciar': [89012345],
  'onuid': [1234567],
  'procurar': [1234567],
  'usuario': [1234567],
  'login': [1234567],
  'link': [1234567],
  'cto': [1234567],
  'vlan': [1234567],
  'wifi': [1234567]
}
mk_link = {
  'ssh': {
    'port': '22',
    'user': 'admin',
    'ip': '255.255.255.255',
    'identity_file': '~/.ssh/id_rsa'
  },
  'script': {
    'first-link': 'linkname-enable',
    'second-link': 'activate-linkname',
    'both-links': 'bothlinksrsc'
  }
}
sqlite_db_path = '/path/to/bot.db'
logs_path = '../logs/'
