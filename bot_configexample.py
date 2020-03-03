#!/usr/bin/env python

# The config file needs to be named 'bot_config.py'
# and be placed on the same directory as the files bot_daemon.py
# and cto_info.py

token = 'bOt-T0keN_ExaMplE'
default_chat = '012345678'
permissions = {
  'autorizar': [1234567, 89012345],
  'authorize': [1234567],
  'sinal': [1234567],
  'reiniciar': [89012345],
  'onuid': [1234567],
  'procurar': [1234567],
  'usuario': [1234567],
  'link': [1234567],
  'cto': [1234567],
  'vlan': [1234567]
}
mk_link = {
  'ssh': {
    'port': '22',
    'user': 'admin',
    'ip': '255.255.255.255'
  },
  'script': {
    'first-link': 'linkname-enable',
    'second-link': 'activate-linkname',
    'both-links': 'bothlinksrsc'
  }
}
sqlite_db_path = '/path/to/bot.db'