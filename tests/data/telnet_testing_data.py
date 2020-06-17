wifi_data_params = {  # this needs to be defined before wifi_data because that can be using some of these params
  'test_a': {
    'board_id': '14',
    'pon_id': '1',
    'onu_number': '4',
    'ssid': '"    WIRELESS NETWORK NAME     "',
    'password': '"    WIRELESS NETWORK PASSWORD    "'
  },
  'test_b': {
    'board_id': '14',
    'pon_id': '1',
    'onu_number': '41',
    'ssid': '',
    'password': ''
  },
  'test_c': {
    'board_id': '14',
    'pon_id': '1',
    'onu_number': '14',
    'ssid': None,
    'password': None
  }
}

wifi_data = {
  'test_a': '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
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
            ''.format(
             ssid=wifi_data_params['test_a']['ssid'],
             password=wifi_data_params['test_a']['password']
            ),
  'test_b': '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
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
            '',
  'test_c': '\r\n----- WIFI SERVICE CONFIG INFO-----\r\n'
            'WIFI :disable\r\n'
            'District:etsi\r\n'
            'Channel:0\r\n'
            'Standard:802.11b\r\n'
            'Tx Power:0\r\n'
            'Working frequency:2.4ghz\r\n'
            'Frequency BW:20mhz/40mhz\r\n'
            '\r\nAdmin\\gpononu# '
            '',
  'default': '',
}
