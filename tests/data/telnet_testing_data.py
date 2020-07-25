test_params = {  # this needs to be defined before wifi_data because that can be using some of these params
  'test_a': {
    'board_id': '14',
    'pon_id': '1',
    'onu_number': '4',
    'ssid': '"    WIRELESS NETWORK NAME     "',
    'password': '"    WIRELESS NETWORK PASSWORD    "',
    'signal_power': '-25.08',
  },
  'test_b': {
    'board_id': '14',
    'pon_id': '1',
    'onu_number': '41',
    'ssid': '',
    'password': '',
    'signal_power': 'off',
  },
  'test_c': {
    'board_id': '14',
    'pon_id': '1',
    'onu_number': '14',
    'ssid': None,
    'password': None,
    'signal_power': 'not found',
  },
  'test_d': {
    'board_id': '12',
    'pon_id': '6',
    'onu_number': '6',
    'ssid': None,
    'password': None,
    'signal_power': 'error',
  },
  'test_e': {
    'board_id': '12',
    'pon_id': '8',
    'onu_number': '18',
    'ssid': None,
    'password': None,
    'signal_power': 'error',
  },
}

test_data = {
  'test_a': {
    'wifi_serv': str(
      '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
      'WIFI :enable\r\n'
      'District:brazil\r\n'
      'Channel:0\r\n'
      'Standard:802.11bgn\r\n'
      'Tx Power:20\r\n'
      'Working frequency:2.4ghz\r\n'
      'Frequency BW:20mhz/40mhz\r\n'
      'SSID Index:1\r\n'
      '**SSID:{ssid}\r\n'
      '**SSID Enable/Disable:enable\r\n'
      '**SSID Hide:disable\r\n'
      '**Wlan Auth Mode:wpa2psk\r\n'
      '**Wlan Encrypt Type:aes\r\n'
      '**WPA Share Key:{password}\r\n'
      '**WPA Key Interval:0\r\n'
      '**RADIUS Server Port:0\r\n'
      '**RADIUS Server Password:\r\n'
      '**WEK Key Lenth:1\r\n'
      '**WEK Key Index:1\r\n'
      '**WEK Key 1:\r\n'
      '**WEK Key 2:\r\n'
      '**WEK Key 3:\r\n'
      '**WEK Key 4:\r\n'
      '**WAPI Server Ip:0\r\n'
      '**WAPI Server Port:0\r\n'
      '**wifi_connect_num :0\r\n'
      '\r\nAdmin\\gpononu# '
    ).format(
        ssid=test_params['test_a']['ssid'],
        password=test_params['test_a']['password'],
      ),
    'optic_module': str(
      "\r\n-----  ONU OPTIC MODULE PAR INFO 10.1.1-----\r\n"
      "NAME          VALUE\tUNIT\r\n"
      "---------------------------------------\r\n"
      "TYPE         : 20\t(KM)\r\n"
      "TEMPERATURE  : 47.00\t('C)\r\n"
      "VOLTAGE      :  3.25\t(V)\r\n"
      "BIAS CURRENT : 18.78\t(mA)\r\n"
      "SEND POWER   :  2.82\t(Dbm)\r\n"
      "RECV POWER   : -25.08\t(Dbm)\r\n"
      "OLT RECV POWER :  0.00\t(Dbm)\r\n"
      "\n\rAdmin\\gpononu# "
    ),
  },
  'test_b': {
    'wifi_serv': str(
      '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
      'WIFI :disable\r\n'
      'District:etsi\r\n'
      'Channel:0\r\n'
      'Standard:802.11b\r\n'
      'Tx Power:0\r\n'
      'Working frequency:2.4ghz\r\n'
      'Frequency BW:20mhz/40mhz\r\n'
      'SSID Index:1\r\n'
      '**SSID:\r\n'
      '**SSID Enable/Disable:disable\r\n'
      '**SSID Hide:disable\r\n'
      '**Wlan Auth Mode:\r\n'
      '**Wlan Encrypt Type:\r\n'
      '**WPA Share Key:\r\n'
      '**WPA Key Interval:0\r\n'
      ' **RADIUS Server Port:0\r\n'
      '**RADIUS Server Password:\r\n'
      '**WEK Key Lenth:0\r\n'
      '**WEK Key Index:0\r\n'
      '**WEK Key 1:\r\n'
      '**WEK Key 2:\r\n'
      '**WEK Key 3:\r\n'
      '**WEK Key 4:\r\n'
      '**WAPI Server Ip:0\r\n'
      '**WAPI Server Port:0\r\n'
      '**wifi_connect_num :0\r\n'
      'SSID Index:2\r\n'
      '**SSID:\r\n'
      'repeat\r\n'
      '\r\nAdmin\\gpononu# '
    ),
    'optic_module': str(
      '\r\n[ ERR -553 ] onu is in unactive!\n\r'
      '\n\rAdmin\\gpononu# '
    ),
  },
  'test_c': {
    'wifi_serv': str(
      '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
      'WIFI :disable\r\n'
      'District:etsi\r\n'
      'Channel:0\r\n'
      'Standard:802.11b\r\n'
      'Tx Power:0\r\n'
      'Working frequency:2.4ghz\r\n'
      'Frequency BW:20mhz/40mhz\r\n'
      '\r\nAdmin\\gpononu# '
    ),
    'optic_module': str(
      '\r\n[ ERR -506 ] the onu is not authorized!\n\r'
      '\n\rAdmin\\gpononu# '
    ),
  },
  'test_d': {
    'wifi_serv': str(
      '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
      'WIFI :disable\r\n'
      'District:etsi\r\n'
      'Channel:0\r\n'
      'Standard:802.11b\r\n'
      'Tx Power:0\r\n'
      'Working frequency:2.4ghz\r\n'
      'Frequency BW:20mhz/40mhz\r\n'
      '\r\nAdmin\\gpononu# '
    ),
    'optic_module': str(
      '\r\n[ ERR 85 ] simulated error \r\n'
      '\n\rAdmin\\gpononu# '
    ),
  },
  'test_e': {
    'wifi_serv': str(
      '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
      'WIFI :disable\r\n'
      'District:etsi\r\n'
      'Channel:0\r\n'
      'Standard:802.11b\r\n'
      'Tx Power:0\r\n'
      'Working frequency:2.4ghz\r\n'
      'Frequency BW:20mhz/40mhz\r\n'
      '\r\nAdmin\\gpononu# '
    ),
    'optic_module': str(
      '\r\nsimulated unknown output\n\r'
      '\n\rAdmin\\gpononu# '
    ),
  },
  'default': {
    'wifi_serv': 'default wifi_data response',
    'optic_module': 'default optic_module response',
    'discovery': 'show discovery slot all link all data',
    'authorization': 'show authorization slot some link some data',
  },
}
