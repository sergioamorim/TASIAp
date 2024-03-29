from tests.mock_classes import MockAuthOnuDevice, MockPon

authorization_list_tests = [
  {
    'authorization_list': str(
      'show authorization slot 14 link 5\r\n'
      '-----  ONU Auth Table ,SLOT=14 PON=5 ,ITEM=0 -----\n\r'
      'Admin\\gpononu# '
    ),
    'last_authorized_number': 0,
  }, {
    'authorization_list': str(
      'show authorization slot 14 link 8\r\n'
      '-----  ONU Auth Table ,SLOT=14 PON=8 ,ITEM=5 -----\n\r'
      'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
      '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
      '  14   8   1 HG260           A up  DGST0edac7ed            , \n\r'
      '  14   8   2 AN5506-01-A1    A up  ITBS1edac7ed            , \n\r'
      '  14   8   3 AN5506-04-F1    A up  FHTT2edac7ed            , \n\r'
      '  14   8   4 AN5506-01-A1    A up  DD1B3edac7ed            , \n\r'
      '  14   8   6 AN5506-01-A1    A up  FHTT4edac7ed            , \n\r'
      '\n\r'
      'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
      'Admin\\gpononu# '
    ),
    'last_authorized_number': 4,
  }, {
    'authorization_list': str(
      'show authorization slot 12 link 8\r\n'
      '-----  ONU Auth Table ,SLOT=12 PON=8 ,ITEM=6 -----\n\r'
      'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
      '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
      '  12   8   1 HG260           A up  DGST5edac7ed            , \n\r'
      '  12   8   2 HG260           A up  DGST6edac7ed            , \n\r'
      '  12   8   3 AN5506-01-A1    A up  ITBS7edac7ed            , \n\r'
      '  12   8   5 AN5506-01-A1    A up  ZNTS8edac7ed            , \n\r'
      '  12   8   6 HG260           A up  DGST9edac7ed            , \n\r'
      '  12   8   8 AN5506-01-A1    A up  OEMTaedac7ed            , \n\r'
      '\n\r'
      'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
      'Admin\\gpononu# '
    ),
    'last_authorized_number': 3,
  }, {
    'authorization_list': str(
      'show authorization slot 12 link 1\r\n'
      '-----  ONU Auth Table ,SLOT=12 PON=1 ,ITEM=54 -----\n\r'
      'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
      '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
      '  12   1   1 AN5506-01-A1    A up  FHTTbedac7ed            , \n\r'
      '  12   1   2 AN5506-01-A1    A up  FHTTcedac7ed            , \n\r'
      '  12   1   3 AN5506-01-A1    A up  FHTTdedac7ed            , \n\r'
      '  12   1   4 AN5506-01-A1    A up  FHTTeedac7ed            , \n\r'
      '  12   1   5 AN5506-01-A1    A up  FHTTfedac7ed            , \n\r'
      '  12   1   6 HG260           A up  DGST10dac7ed            , \n\r'
      '  12   1   7 HG260           A up  DGST11dac7ed            , \n\r'
      '  12   1   8 HG260           A up  DGST12dac7ed            , \n\r'
      '  12   1   9 AN5506-01-A1    A up  FHTT13dac7ed            , \n\r'
      '  12   1  10 HG260           A up  DGST14dac7ed            , \n\r'
      '  12   1  11 AN5506-01-A1    A up  ZNTS15dac7ed            , \n\r'
      '  12   1  12 HG260           A up  ZNTS16dac7ed            , \n\r'
      '  12   1  13 AN5506-01-A1    A up  ITBS17dac7ed            , \n\r'
      '  12   1  14 AN5506-01-A1    A up  DD1618dac7ed            , \n\r'
      '  12   1  15 AN5506-01-A1    A up  FHTT19dac7ed            , \n\r'
      '  12   1  16 AN5506-SFU      A dn  NULL11161116            , \n\r'
      '  12   1  17 AN5506-01-A1    A up  ZNTS1adac7ed            , \n\r'
      '  12   1  18 AN5506-01-A1    A up  FHTT1bdac7ed            , \n\r'
      '  12   1  19 HG260           A up  ZNTS1cdac7ed            , \n\r'
      '  12   1  20 AN5506-01-A1    A up  DD161ddac7ed            , \n\r'
      '  12   1  21 AN5506-01-A1    A up  HDVG1edac7ed            , \n\r'
      '  12   1  22 AN5506-01-A1    A up  ITBS1fdac7ed            , \n\r'
      '  12   1  23 AN5506-01-A1    A up  FHTT20dac7ed            , \n\r'
      '  12   1  24 HG260           A up  DGST21dac7ed            , \n\r'
      '  12   1  25 HG260           A up  ZNTS22dac7ed            , \n\r'
      '  12   1  26 AN5506-01-A1    A up  ZNTS23dac7ed            , \n\r'
      '  12   1  27 HG260           A up  ZNTS24dac7ed            , \n\r'
      '  12   1  28 AN5506-01-A1    A up  DD1625dac7ed            , \n\r'
      '  12   1  29 AN5506-01-A1    A up  ITBS26dac7ed            , \n\r'
      '  12   1  30 AN5506-01-A1    A up  DD1627dac7ed            , \n\r'
      '  12   1  31 AN5506-01-A1    A up  DD1628dac7ed            , \n\r'
      '  12   1  32 AN5506-01-A1    A up  FHTT29dac7ed            , \n\r'
      '  12   1  34 AN5506-01-A1    A up  OEMT2adac7ed            , \n\r'
      '  12   1  35 AN5506-01-A1    A up  OEMT2bdac7ed            , \n\r'
      '  12   1  36 AN5506-01-A1    A up  OEMT2cdac7ed            , \n\r'
      '  12   1  37 AN5506-01-A1    A up  ITBS2ddac7ed            , \n\r'
      '  12   1  38 AN5506-01-A1    A up  FHTT2edac7ed            , \n\r'
      '  12   1  39 AN5506-01-A1    A up  FHTT2fdac7ed            , \n\r'
      '  12   1  40 AN5506-01-A1    A up  ITBS30dac7ed            , \n\r'
      '  12   1  41 AN5506-01-A1    A up  ITBS31dac7ed            , \n\r'
      '  12   1  42 AN5506-01-A1    A up  DD1B32dac7ed            , \n\r'
      '  12   1  43 AN5506-01-A1    A up  DD1B33dac7ed            , \n\r'
      '  12   1  44 AN5506-01-A1    A up  DD7234dac7ed            , \n\r'
      '  12   1  47 AN5506-01-A1    A up  ITBS35dac7ed            , \n\r'
      '  12   1  48 AN5506-01-A1    A up  ITBS36dac7ed            , \n\r'
      '  12   1  49 AN5506-01-A1    A up  FHTT37dac7ed            , \n\r'
      '  12   1  50 HG260           A up  PACE38dac7ed            , \n\r'
      '  12   1  51 AN5506-01-A1    A up  FHTT39dac7ed            , \n\r'
      '  12   1  52 AN5506-01-A1    A up  FHTT3adac7ed            , \n\r'
      '  12   1  53 HG260           A up  PACE3bdac7ed            , \n\r'
      '  12   1  54 HG260           A up  ZNTS3cdac7ed            , \n\r'
      '  12   1  55 AN5506-01-A1    A up  FHTT3ddac7ed            , \n\r'
      '  12   1  57 AN5506-01-A1    A up  FHTT3edac7ed            , \n\r'
      '  12   1  58 AN5506-01-A1    A up  FHTT3fdac7ed            , \n\r'
      '\n\r'
      'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
      'Admin\\gpononu# '
    ),
    'last_authorized_number': 32,
  }, {
    'authorization_list': str(
      'show authorization slot 14 link 1\r\n'
      '-----  ONU Auth Table ,SLOT=14 PON=1 ,ITEM=23 -----\n\r'
      'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
      '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
      '  14   1   1 HG260           A up  DGST40dac7ed            , \n\r'
      '  14   1   2 AN5506-01-A1    A up  ITBS41dac7ed            , \n\r'
      '  14   1   3 HG260           A up  ZNTS42dac7ed            , \n\r'
      '  14   1   4 AN5506-04-F1    A up  FHTT43dac7ed            , \n\r'
      '  14   1   5 AN5506-01-A1    A up  DD1644dac7ed            , \n\r'
      '  14   1   6 HG260           A up  DGST45dac7ed            , \n\r'
      '  14   1   7 AN5506-01-A1    A up  FHTT46dac7ed            , \n\r'
      '  14   1   8 AN5506-01-A1    A up  DD1647dac7ed            , \n\r'
      '  14   1   9 AN5506-01-A1    A up  FHTT48dac7ed            , \n\r'
      '  14   1  10 HG260           A up  ZNTS49dac7ed            , \n\r'
      '  14   1  11 AN5506-01-A1    A up  DD164adac7ed            , \n\r'
      '  14   1  12 AN5506-01-A1    A up  ITBS4bdac7ed            , \n\r'
      '  14   1  13 HG260           A up  ZNTS4cdac7ed            , \n\r'
      '  14   1  14 AN5506-04-F1    A up  FHTT4ddac7ed            , \n\r'
      '  14   1  15 AN5506-01-A1    A up  FHTT4edac7ed            , \n\r'
      '  14   1  17 HG260           A up  ZNTS4fdac7ed            , \n\r'
      '  14   1  18 AN5506-01-A1    A up  ITBS50dac7ed            , \n\r'
      '  14   1  19 AN5506-01-A1    A up  ITBS51dac7ed            , \n\r'
      '  14   1  20 AN5506-01-A1    A up  FHTT52dac7ed            , \n\r'
      '  14   1  21 AN5506-01-A1    A up  ITBS53dac7ed            , \n\r'
      '  14   1  22 HG260           A dn  PACE54dac7ed            , \n\r'
      '  14   1  23 AN5506-01-A1    A up  FHTT55dac7ed            , \n\r'
      '  14   1  24 AN5506-01-A1    A up  FHTT56dac7ed            , \n\r'
      '\n\r'
      'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
      'Admin\\gpononu# '
    ),
    'last_authorized_number': 15,
  }, {
    'authorization_list': str(
      'show authorization slot 14 link 7\r\n-----  ONU Auth Table ,SLOT=14 PON=7 ,ITEM=3 -----\n\r'
      'SLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN PWD\n\r'
      '---- --- --- -------------- -- --- ------------ ---------- --------------------\n\r'
      '  14   7   1 HG260           A up  DGST57dac7ed            , \n\r'
      '  14   7   2 HG260           A up  PACE58dac7ed            , \n\r'
      '  14   7   3 AN5506-01-A1    A up  FHTT59dac7ed            , \n\r'
      '\n\r'
      'A: Authorized  P: Preauthorized  R: System Reserved\n\r'
      'Admin\\gpononu# '
    ),
    'last_authorized_number': 3,
  }, {
    'authorization_list': 'show authorization slot 14 link',
    'last_authorized_number': None,
  }, {
    'authorization_list': 'show authorization slot 14 link 7\r\n-----  ONU Auth Table ,SLOT=14 PON=7 ,ITEM',
    'last_authorized_number': None,
  },
]

discovery_lists_tests = [
  {
    'discovery_list': str(
      'show discovery slot all link all\r\n'
      '-----  ONU Unauth Table ,SLOT=12 PON=1 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=8 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=1 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=8 ,ITEM=0-----\n\r'
      'Admin\\gpononu# '
    ),
    'onu_list': [],
    'onu_tuples_tests': [],
  },
  {
    'discovery_list': str(
      'show discovery slot all link all\r\n'
      '-----  ONU Unauth Table ,SLOT=12 PON=1 ,ITEM=1-----\n\r'
      'NO       TYPE           PHY_ID        PWD           SN LOID, SN PWD\n\r'
      '--  --------------  ------------  ----------  --------------------------\n\r'
      '01  HG260           ZNTSa0b1c2d2              , \n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=8 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=1 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=8 ,ITEM=0-----\n\r'
      'Admin\\gpononu# '
    ),
    'onu_list': [
      MockAuthOnuDevice(
        authorization_id='1',
        onu_type='hg260',
        phy_id='ZNTSa0b1c2d2',
        pon=MockPon(pon_id='1', board_id='12')
      ),
    ],
    'onu_tuples_tests': [
      {
        'board_id': '12',
        'item_quantity': 1,
        'pon_id': '1',
        'onu_tuples': [('01', 'HG260', 'ZNTSa0b1c2d2')],
        'onus_list_textual': '01  HG260           ZNTSa0b1c2d2              , \n',
        'onus_from_pon_textual_pattern': 'SLOT=12 PON=1 ,ITEM=1[-\nA-Z\\s_,]*([-\n\r\\s_,A-Za-z0-9]*)(-{5}|Admin)',
      },
    ],
  },
  {
    'discovery_list': str(
      'show discovery slot all link all\r\n'
      '-----  ONU Unauth Table ,SLOT=12 PON=1 ,ITEM=2-----\n\r'
      'NO       TYPE           PHY_ID        PWD           SN LOID, SN PWD\n\r'
      '--  --------------  ------------  ----------  --------------------------\n\r'
      '01  HG260           ZNTSa0b1c2d3              , \n\r'
      '02  AN5506-01-A1    DD16a0b1c2d4              , \n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=8 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=1 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=8 ,ITEM=0-----\n\r'
      'Admin\\gpononu# '
    ),
    'onu_list': [
      MockAuthOnuDevice(
        authorization_id='1',
        onu_type='hg260',
        phy_id='ZNTSa0b1c2d3',
        pon=MockPon(pon_id='1', board_id='12')
      ),
      MockAuthOnuDevice(
        authorization_id='2',
        onu_type='5506-01-a1',
        phy_id='DD16a0b1c2d4',
        pon=MockPon(pon_id='1', board_id='12')
      ),
    ],
    'onu_tuples_tests': [
      {
        'board_id': '12',
        'item_quantity': 2,
        'pon_id': '1',
        'onu_tuples': [('01', 'HG260', 'ZNTSa0b1c2d3'), ('02', 'AN5506-01-A1', 'DD16a0b1c2d4')],
        'onus_list_textual': str(
          '01  HG260           ZNTSa0b1c2d3              , \n'
          '02  AN5506-01-A1    DD16a0b1c2d4              , \n'
        ),
        'onus_from_pon_textual_pattern': 'SLOT=12 PON=1 ,ITEM=2[-\nA-Z\\s_,]*([-\n\r\\s_,A-Za-z0-9]*)(-{5}|Admin)',
      },
    ],
  },
  {
    'discovery_list': str(
      'show discovery slot all link all\r\n'
      '-----  ONU Unauth Table ,SLOT=12 PON=1 ,ITEM=1-----\n\r'
      'NO       TYPE           PHY_ID        PWD           SN LOID, SN PWD\n\r'
      '--  --------------  ------------  ----------  --------------------------\n\r'
      '01  HG260           ZNTSa0b1c2d5              , \n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=12 PON=8 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=1 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=2 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=3 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=4 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=5 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=6 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=7 ,ITEM=0-----\n\r'
      '-----  ONU Unauth Table ,SLOT=14 PON=8 ,ITEM=2-----\n\r'
      'NO       TYPE           PHY_ID        PWD           SN LOID, SN PWD\n\r'
      '--  --------------  ------------  ----------  --------------------------\n\r'
      '01  AN5506-01-A1    DD16a0b1c2d6              , \n\r'
      '02  AN5506-01-A1    DD16a0b1c2d7              , \n\r'
      'Admin\\gpononu# '
    ),
    'onu_list': [
      MockAuthOnuDevice(
        authorization_id='1',
        onu_type='hg260',
        phy_id='ZNTSa0b1c2d5',
        pon=MockPon(pon_id='1', board_id='12')
      ),
      MockAuthOnuDevice(
        authorization_id='1',
        onu_type='5506-01-a1',
        phy_id='DD16a0b1c2d6',
        pon=MockPon(pon_id='8', board_id='14')
      ),
      MockAuthOnuDevice(
        authorization_id='2',
        onu_type='5506-01-a1',
        phy_id='DD16a0b1c2d7',
        pon=MockPon(pon_id='8', board_id='14')
      ),
    ],
    'onu_tuples_tests': [
      {
        'board_id': '12',
        'item_quantity': 1,
        'pon_id': '1',
        'onu_tuples': [
          ('01', 'HG260', 'ZNTSa0b1c2d5'),
        ],
        'onus_list_textual': '01  HG260           ZNTSa0b1c2d5              , \n',
        'onus_from_pon_textual_pattern': 'SLOT=12 PON=1 ,ITEM=1[-\nA-Z\\s_,]*([-\n\r\\s_,A-Za-z0-9]*)(-{5}|Admin)',
      },
      {
        'board_id': '14',
        'item_quantity': 2,
        'pon_id': '8',
        'onu_tuples': [
          ('01', 'AN5506-01-A1', 'DD16a0b1c2d6'),
          ('02', 'AN5506-01-A1', 'DD16a0b1c2d7'),
        ],
        'onus_list_textual': str(
          '01  AN5506-01-A1    DD16a0b1c2d6              , \n'
          '02  AN5506-01-A1    DD16a0b1c2d7              , \n'
        ),
        'onus_from_pon_textual_pattern': 'SLOT=14 PON=8 ,ITEM=2[-\nA-Z\\s_,]*([-\n\r\\s_,A-Za-z0-9]*)(-{5}|Admin)',
      },
    ]
  },
]
