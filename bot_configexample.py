#!/usr/bin/env python

# The config file needs to be named 'bot_config.py'
# and be placed on the same directory as the files bot_daemon.py
# and cto_info.py

token = 'bOt-T0keN_ExaMplE'
authorized_users = [01234567, 89012345]
default_chat = '012345678'
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

