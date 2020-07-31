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

show_pon_mac = {
  'data': str(
    'show pon_mac slot 12 link 1\r\n'
    '-----  PON MAC ADDRESS, ITEM=32 -----\n\r'
    '001\t00:1A:3F:86:EC:0A\t Vid:1100\t OnuId:26\n\r'
    '002\t00:1A:3F:E8:45:28\t Vid:1100\t OnuId:10\n\r'
    '003\tE4:BE:ED:9B:26:9F\t Vid:1100\t OnuId:7\n\r'
    '004\tE4:BE:ED:A2:2E:7E\t Vid:1100\t OnuId:25\n\r'
    '005\tE8:65:D4:38:80:58\t Vid:1100\t OnuId:30\n\r'
    '006\t58:10:8C:26:DC:30\t Vid:1101\t OnuId:1\n\r'
    '007\t58:10:8C:46:8D:67\t Vid:1101\t OnuId:1\n\r'
    '008\t58:10:8C:B0:E9:8E\t Vid:1101\t OnuId:1\n\r'
    '009\t78:44:76:8F:BB:07\t Vid:1101\t OnuId:1\n\r'
    '010\t78:44:76:90:65:0F\t Vid:1101\t OnuId:1\n\r'
    '011\t78:44:76:90:C1:27\t Vid:1101\t OnuId:1\n\r'
    '012\tC4:6E:1F:AC:76:27\t Vid:1101\t OnuId:1\n\r'
    '013\tC8:3A:35:7C:FE:30\t Vid:1101\t OnuId:1\n\r'
    '014\tE4:BE:ED:1B:64:1B\t Vid:1101\t OnuId:1\n\r'
    '015\tEC:08:6B:88:74:F3\t Vid:1101\t OnuId:1\n\r'
    '016\t00:1A:3F:7D:15:C8\t Vid:1102\t OnuId:2\n\r'
    '017\t00:1A:3F:FA:B1:10\t Vid:1102\t OnuId:2\n\r'
    '018\tC8:E7:D8:87:84:59\t Vid:1102\t OnuId:2\n\r'
    '019\t00:72:63:0E:9D:6B\t Vid:1103\t OnuId:3\n\r'
    '020\tC8:3A:35:C8:A6:A8\t Vid:1103\t OnuId:3\n\r'
    '021\t00:1A:3F:24:F3:A2\t Vid:1104\t OnuId:4\n\r'
    '022\t00:1A:3F:85:D2:23\t Vid:1104\t OnuId:4\n\r'
    '023\t00:1A:3F:1F:9D:F1\t Vid:1105\t OnuId:5\n\r'
    '024\tF4:F2:6D:AF:5E:3B\t Vid:1105\t OnuId:5\n\r'
    '025\tE4:BE:ED:60:23:8D\t Vid:1106\t OnuId:6\n\r'
    '026\tE4:BE:ED:A1:DD:2F\t Vid:1109\t OnuId:9\n\r'
    '027\tE4:BE:ED:A2:12:C7\t Vid:1109\t OnuId:9\n\r'
    '028\tC8:3A:35:A1:D6:A0\t Vid:1115\t OnuId:15\n\r'
    '029\tE4:BE:ED:8F:91:9E\t Vid:1119\t OnuId:19\n\r'
    '030\tC8:3A:35:32:0C:E8\t Vid:1135\t OnuId:35\n\r'
    '031\tCC:06:77:69:DC:B1\t Vid:4087\t OnuId:33\n\r'
    '032\t22:3E:44:55:66:11\t Vid:4091\t OnuId:65535\n\r'
    'Admin\\gponline# '
  ),
  'macs_from_onu': {
    '25': ['E4:BE:ED:A2:2E:7E'],
    '26': ['00:1A:3F:86:EC:0A'],
    '99': [],
    '1': [
      '58:10:8C:26:DC:30',
      '58:10:8C:46:8D:67',
      '58:10:8C:B0:E9:8E',
      '78:44:76:8F:BB:07',
      '78:44:76:90:65:0F',
      '78:44:76:90:C1:27',
      'C4:6E:1F:AC:76:27',
      'C8:3A:35:7C:FE:30',
      'E4:BE:ED:1B:64:1B',
      'EC:08:6B:88:74:F3',
    ],
  },
}
