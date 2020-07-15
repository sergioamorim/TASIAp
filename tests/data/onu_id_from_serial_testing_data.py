complete_auth_table = str(  # this is actually encoded as ASCII binary data
  'show authorization slot all link all\r\n'
  '-----  ONU Auth Table ,SLOT=12 PON=1 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=2 ,ITEM=1 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  12   2   1 HG260           A up  TPLG8edac7ed            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=3 ,ITEM=2 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  12   3   1 HG260           A up  DGST8edac7ee            , \n\r'
  '  12   3   2 AN5506-01-A1    A up  ITBS8edac7ef            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=4 ,ITEM=9 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  12   4   1 AN5506-SFU      A dn  NULL14011401            , \n\r'
  '  12   4   2 HG260           A up  TPLG8edac7f0            , \n\r'
  '  12   4   3 HG260           A up  TPLG8edac7f1            , \n\r'
  '  12   4   4 HG260           A up  TPLG8edac7f2            , \n\r'
  '  12   4   5 HG260           A up  DGST8edac7f3            , \n\r'
  '  12   4   6 HG260           A up  DGST8edac7f4            , \n\r'
  '  12   4   7 HG260           A up  DGST8edac7f5            , \n\r'
  '  12   4   8 AN5506-01-A1    A up  ITBS8edac7f6            , \n\r'
  '  12   4   9 AN5506-01-A1    A up  ITBS8edac7f7            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=5 ,ITEM=10 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  12   5   1 AN5506-01-A1    A up  FHTT8edac7f8            , \n\r'
  '  12   5   2 AN5506-01-A1    A up  FHTT8edac7f9            , \n\r'
  '  12   5   3 AN5506-01-A1    A up  FHTT8edac7fa            , \n\r'
  '  12   5   4 HG260           A up  TPLG8edac7fb            , \n\r'
  '  12   5   5 AN5506-01-A1    A up  DD1B8edac7fc            , \n\r'
  '  12   5   6 AN5506-SFU      A dn  NULL15061506            , \n\r'
  '  12   5   7 HG260           A up  FHTT8edac7fd            , \n\r'
  '  12   5   8 HG260           A up  DGST8edac7fe            , \n\r'
  '  12   5   9 HG260           A up  DGST8edac7ff            , \n\r'
  '  12   5  10 HG260           A up  DGST8edac800            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=6 ,ITEM=11 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  12   6   1 AN5506-01-A1    A up  DD168edac801            , \n\r'
  '  12   6   2 HG260           A up  FHTT8edac802            , \n\r'
  '  12   6   3 AN5506-01-A1    A up  ITBS8edac803            , \n\r'
  '  12   6   4 AN5506-01-A1    A up  ITBS8edac804            , \n\r'
  '  12   6   5 HG260           A up  FHTT8edac805            , \n\r'
  '  12   6   6 HG260           A up  FHTT8edac806            , \n\r'
  '  12   6   7 AN5506-01-A1    A up  ITBS8edac807            , \n\r'
  '  12   6   8 AN5506-01-A1    A up  FHTT8edac808            , \n\r'
  '  12   6   9 AN5506-04-F1    A up  FHTT8edac809            , \n\r'
  '  12   6  10 AN5506-01-A1    A up  ZNTS8edac80a            , \n\r'
  '  12   6  11 AN5506-01-A1    A up  OEMT8edac80b            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=7 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=8 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=1 ,ITEM=1 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  14   1   1 HG260           A up  DGST8edac80c            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=2 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=3 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=4 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=5 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=6 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=7 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=8 ,ITEM=5 -----\n\r'
  'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
  '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
  '  14   8   1 HG260           A up  DGST8edac80d            , \n\r'
  '  14   8   2 AN5506-01-A1    A up  ITBS8edac80e            , \n\r'
  '  14   8   3 AN5506-04-F1    A up  FHTT8edac80f            , \n\r'
  '  14   8   4 AN5506-01-A1    A up  DD1B8edac810            , \n\r'
  '  14   8   6 AN5506-01-A1    A dn  FHTT8edac811            , \n\r'
  '\n\r'
  'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
  'Admin\\gpononu# '
).encode('ascii')

empty_auth_table = str(  # this is encoded as ASCII binary data
  'show authorization slot all link all\r\n'
  '-----  ONU Auth Table ,SLOT=12 PON=1 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=2 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=3 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=4 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=5 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=6 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=7 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=12 PON=8 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=1 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=2 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=3 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=4 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=5 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=6 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=7 ,ITEM=0 -----\n\r'
  '-----  ONU Auth Table ,SLOT=14 PON=8 ,ITEM=0 -----\n\r'
  'Admin\\gpononu# '
).encode('ascii')

test_cases = [
  {
    'auth_table': empty_auth_table,
    'onus': []
  },
  {
    'auth_table': complete_auth_table,
    'onus': [
      {
        'serial': 'INVA11d38808',
        'onu_info': None
      },
      {
        'serial': 'TPLG8edac7ed',
        'onu_info': {
          'onu_id': '1201',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac7ee',
        'onu_info': {
          'onu_id': '1301',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac7ef',
        'onu_info': {
          'onu_id': '1302',
          'state': 'up'
        }
      },
      {
        'serial': 'NULL14011401',
        'onu_info': {
          'onu_id': '1401',
          'state': 'dn'
        }
      },
      {
        'serial': 'TPLG8edac7f0',
        'onu_info': {
          'onu_id': '1402',
          'state': 'up'
        }
      },
      {
        'serial': 'TPLG8edac7f1',
        'onu_info': {
          'onu_id': '1403',
          'state': 'up'
        }
      },
      {
        'serial': 'TPLG8edac7f2',
        'onu_info': {
          'onu_id': '1404',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac7f3',
        'onu_info': {
          'onu_id': '1405',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac7f4',
        'onu_info': {
          'onu_id': '1406',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac7f5',
        'onu_info': {
          'onu_id': '1407',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac7f6',
        'onu_info': {
          'onu_id': '1408',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac7f7',
        'onu_info': {
          'onu_id': '1409',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac7f8',
        'onu_info': {
          'onu_id': '1501',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac7f9',
        'onu_info': {
          'onu_id': '1502',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac7fa',
        'onu_info': {
          'onu_id': '1503',
          'state': 'up'
        }
      },
      {
        'serial': 'TPLG8edac7fb',
        'onu_info': {
          'onu_id': '1504',
          'state': 'up'
        }
      },
      {
        'serial': 'DD1B8edac7fc',
        'onu_info': {
          'onu_id': '1505',
          'state': 'up'
        }
      },
      {
        'serial': 'NULL15061506',
        'onu_info': {
          'onu_id': '1506',
          'state': 'dn'
        }
      },
      {
        'serial': 'FHTT8edac7fd',
        'onu_info': {
          'onu_id': '1507',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac7fe',
        'onu_info': {
          'onu_id': '1508',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac7ff',
        'onu_info': {
          'onu_id': '1509',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac800',
        'onu_info': {
          'onu_id': '1510',
          'state': 'up'
        }
      },
      {
        'serial': 'DD168edac801',
        'onu_info': {
          'onu_id': '1601',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac802',
        'onu_info': {
          'onu_id': '1602',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac803',
        'onu_info': {
          'onu_id': '1603',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac804',
        'onu_info': {
          'onu_id': '1604',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac805',
        'onu_info': {
          'onu_id': '1605',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac806',
        'onu_info': {
          'onu_id': '1606',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac807',
        'onu_info': {
          'onu_id': '1607',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac808',
        'onu_info': {
          'onu_id': '1608',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac809',
        'onu_info': {
          'onu_id': '1609',
          'state': 'up'
        }
      },
      {
        'serial': 'ZNTS8edac80a',
        'onu_info': {
          'onu_id': '1610',
          'state': 'up'
        }
      },
      {
        'serial': 'OEMT8edac80b',
        'onu_info': {
          'onu_id': '1611',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac80c',
        'onu_info': {
          'onu_id': '2101',
          'state': 'up'
        }
      },
      {
        'serial': 'DGST8edac80d',
        'onu_info': {
          'onu_id': '2801',
          'state': 'up'
        }
      },
      {
        'serial': 'ITBS8edac80e',
        'onu_info': {
          'onu_id': '2802',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac80f',
        'onu_info': {
          'onu_id': '2803',
          'state': 'up'
        }
      },
      {
        'serial': 'DD1B8edac810',
        'onu_info': {
          'onu_id': '2804',
          'state': 'up'
        }
      },
      {
        'serial': 'FHTT8edac811',
        'onu_info': {
          'onu_id': '2806',
          'state': 'dn'
        }
      },
    ]
  }
]
