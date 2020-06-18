from unittest import TestCase, main

from tasiap.authorize_onu import format_onu_type, get_last_authorized_number


class TestStringFunctions(TestCase):

  def test_format_onu_type(self):
    onu_type_a = 'AN5506-01-A1'
    onu_type_b = 'AN5506-04-F1'
    onu_type_c = 'HG260'

    self.assertEqual(format_onu_type(onu_type_a), '5506-01-a1')
    self.assertEqual(format_onu_type(onu_type_b), '5506-04-f1')
    self.assertEqual(format_onu_type(onu_type_c), 'hg260')

  def test_get_last_authorized_number(self):
    authorization_list_a = 'show authorization slot 14 link 5\r\n-----  ONU Auth Table ,SLOT=14 PON=5 ,ITEM=0 ' \
                           '-----\n\rAdmin\\gpononu# '
    authorization_list_b = 'show authorization slot 14 link 8\r\n-----  ONU Auth Table ,SLOT=14 PON=8 ,ITEM=5 ' \
                           '-----\n\rSLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN ' \
                           'PWD\n\r---- --- --- -------------- -- --- ------------ ---------- ' \
                           '--------------------\n\r  14   8   1 HG260           A up  DGST21402475            , ' \
                           '\n\r  14   8   2 AN5506-01-A1    A up  ITBS2c9f2c0a            , \n\r  14   8   3 ' \
                           'AN5506-04-F1    A up  FHTT11694380            , \n\r  14   8   4 AN5506-01-A1    A up  ' \
                           'DD1Bb3cd8c40            , \n\r  14   8   6 AN5506-01-A1    A up  FHTT0002ca72            ' \
                           ', \n\r\n\rA: Authorized  P: Preauthorized  R: System Reserved\n\rAdmin\\gpononu# '
    authorization_list_c = 'show authorization slot 12 link 8\r\n-----  ONU Auth Table ,SLOT=12 PON=8 ,ITEM=6 ' \
                           '-----\n\rSLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN ' \
                           'PWD\n\r---- --- --- -------------- -- --- ------------ ---------- ' \
                           '--------------------\n\r  12   8   1 HG260           A up  DGST21401d22            , ' \
                           '\n\r  12   8   2 HG260           A up  DGST21402479            , \n\r  12   8   3 ' \
                           'AN5506-01-A1    A up  ITBS2c97a41d            , \n\r  12   8   5 AN5506-01-A1    A up  ' \
                           'ZNTS2c221959            , \n\r  12   8   6 HG260           A up  DGST21401f7a            ' \
                           ', \n\r  12   8   8 AN5506-01-A1    A up  OEMT3c02c874            , \n\r\n\rA: ' \
                           'Authorized  P: Preauthorized  R: System Reserved\n\rAdmin\\gpononu# '
    authorization_list_d = 'show authorization slot 12 link 1\r\n-----  ONU Auth Table ,SLOT=12 PON=1 ,ITEM=54 ' \
                           '-----\n\rSLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN ' \
                           'PWD\n\r---- --- --- -------------- -- --- ------------ ---------- ' \
                           '--------------------\n\r  12   1   1 AN5506-01-A1    A up  FHTT00015116            , ' \
                           '\n\r  12   1   2 AN5506-01-A1    A up  FHTT00001ffc            , \n\r  12   1   3 ' \
                           'AN5506-01-A1    A up  FHTT00003a8d            , \n\r  12   1   4 AN5506-01-A1    A up  ' \
                           'FHTT00001ff1            , \n\r  12   1   5 AN5506-01-A1    A up  FHTT0000223d            ' \
                           ', \n\r  12   1   6 HG260           A up  DGST21402476            , \n\r  12   1   7 ' \
                           'HG260           A up  DGST21401ce5            , \n\r  12   1   8 HG260           A up  ' \
                           'DGST21401cf7            , \n\r  12   1   9 AN5506-01-A1    A up  ' \
                           'FHTT00015620            , \n\r  12   1  10 HG260           A up  DGST2140247d            ' \
                           ', \n\r  12   1  11 AN5506-01-A1    A up  ZNTS2c572c14            , \n\r  12   1  12 ' \
                           'HG260           A up  ZNTS2c0104ed            , \n\r  12   1  13 AN5506-01-A1    A up  ' \
                           'ITBS2cbeeb35            , \n\r  12   1  14 AN5506-01-A1    A up  DD16b3675b52            ' \
                           ', \n\r  12   1  15 AN5506-01-A1    A up  FHTT0001476e            , \n\r  12   1  16 ' \
                           'AN5506-SFU      A dn  NULL11161116            , \n\r  12   1  17 AN5506-01-A1    A up  ' \
                           'ZNTS2c572c24            , \n\r  12   1  18 AN5506-01-A1    A up  FHTT00015113            ' \
                           ', \n\r  12   1  19 HG260           A up  ZNTS2c0105db            , \n\r  12   1  20 ' \
                           'AN5506-01-A1    A up  DD16b3675afc            , \n\r  12   1  21 AN5506-01-A1    A up  ' \
                           'HDVG290f6539            , \n\r  12   1  22 AN5506-01-A1    A up  ITBS2c941d43            ' \
                           ', \n\r  12   1  23 AN5506-01-A1    A up  FHTT00025baa            , \n\r  12   1  24 ' \
                           'HG260           A up  DGST21402481            , \n\r  12   1  25 HG260           A up  ' \
                           'ZNTS8ca81005            , \n\r  12   1  26 AN5506-01-A1    A up  ZNTS2c572f3a            ' \
                           ', \n\r  12   1  27 HG260           A up  ZNTS2c010033            , \n\r  12   1  28 ' \
                           'AN5506-01-A1    A up  DD16b36716b4            , \n\r  12   1  29 AN5506-01-A1    A up  ' \
                           'ITBS2cbeef5d            , \n\r  12   1  30 AN5506-01-A1    A up  DD16b366ca1c            ' \
                           ', \n\r  12   1  31 AN5506-01-A1    A up  DD16b366b850            , \n\r  12   1  32 ' \
                           'AN5506-01-A1    A up  FHTT00025b13            , \n\r  12   1  34 AN5506-01-A1    A up  ' \
                           'OEMT3c02cff7            , \n\r  12   1  35 AN5506-01-A1    A up  OEMT3c02cca6            ' \
                           ', \n\r  12   1  36 AN5506-01-A1    A up  OEMT3c02c82b            , \n\r  12   1  37 ' \
                           'AN5506-01-A1    A up  ITBS2cbeeb39            , \n\r  12   1  38 AN5506-01-A1    A up  ' \
                           'FHTT000362a7            , \n\r  12   1  39 AN5506-01-A1    A up  FHTT0002be07            ' \
                           ', \n\r  12   1  40 AN5506-01-A1    A up  ITBS2cd38a2e            , \n\r  12   1  41 ' \
                           'AN5506-01-A1    A up  ITBS0d2be6fd            , \n\r  12   1  42 AN5506-01-A1    A up  ' \
                           'DD1Bb3d10387            , \n\r  12   1  43 AN5506-01-A1    A up  DD1Bb3d108ad            ' \
                           ', \n\r  12   1  44 AN5506-01-A1    A up  DD72b3ddc3e9            , \n\r  12   1  47 ' \
                           'AN5506-01-A1    A up  ITBS2cdb99a9            , \n\r  12   1  48 AN5506-01-A1    A up  ' \
                           'ITBS2cdbd1a1            , \n\r  12   1  49 AN5506-01-A1    A up  FHTT000399e4            ' \
                           ', \n\r  12   1  50 HG260           A up  PACEd8a7bf6f            , \n\r  12   1  51 ' \
                           'AN5506-01-A1    A up  FHTT000362b1            , \n\r  12   1  52 AN5506-01-A1    A up  ' \
                           'FHTT000399ed            , \n\r  12   1  53 HG260           A up  PACE586dba0d            ' \
                           ', \n\r  12   1  54 HG260           A up  ZNTS8ca19484            , \n\r  12   1  55 ' \
                           'AN5506-01-A1    A up  FHTT0003ed34            , \n\r  12   1  57 AN5506-01-A1    A up  ' \
                           'FHTT00043944            , \n\r  12   1  58 AN5506-01-A1    A up  FHTT00035d31            ' \
                           ', \n\r\n\rA: Authorized  P: Preauthorized  R: System Reserved\n\rAdmin\\gpononu# '
    authorization_list_e = 'show authorization slot 14 link 1\r\n-----  ONU Auth Table ,SLOT=14 PON=1 ,ITEM=23 ' \
                           '-----\n\rSLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN ' \
                           'PWD\n\r---- --- --- -------------- -- --- ------------ ---------- ' \
                           '--------------------\n\r  14   1   1 HG260           A up  DGST21401cfc            ' \
                           ', \n\r  14   1   2 AN5506-01-A1    A up  ITBS0d2be70d            , \n\r  14   1   3 ' \
                           'HG260           A up  ZNTS2c213af9            , \n\r  14   1   4 AN5506-04-F1    A up  ' \
                           'FHTT1177bc38            , \n\r  14   1   5 AN5506-01-A1    A up  DD16b3674b46            ' \
                           ', \n\r  14   1   6 HG260           A up  DGST21402478            , \n\r  14   1   7 ' \
                           'AN5506-01-A1    A up  FHTT00023fc5            , \n\r  14   1   8 AN5506-01-A1    A up  ' \
                           'DD16b3675b1a            , \n\r  14   1   9 AN5506-01-A1    A up  FHTT0001561d            ' \
                           ', \n\r  14   1  10 HG260           A up  ZNTS2c213a1d            , \n\r  14   1  11 ' \
                           'AN5506-01-A1    A up  DD16b348c23a            , \n\r  14   1  12 AN5506-01-A1    A up  ' \
                           'ITBS2cdb17c1            , \n\r  14   1  13 HG260           A up  ZNTS3f97c5fd            ' \
                           ', \n\r  14   1  14 AN5506-04-F1    A up  FHTT10d63a88            , \n\r  14   1  15 ' \
                           'AN5506-01-A1    A up  FHTT000241dd            , \n\r  14   1  17 HG260           A up  ' \
                           'ZNTS2c221aa7            , \n\r  14   1  18 AN5506-01-A1    A up  ITBS2c7ca7a3            ' \
                           ', \n\r  14   1  19 AN5506-01-A1    A up  ITBS2c975f35            , \n\r  14   1  20 ' \
                           'AN5506-01-A1    A up  FHTT00025b1f            , \n\r  14   1  21 AN5506-01-A1    A up  ' \
                           'ITBS2cbeeb05            , \n\r  14   1  22 HG260           A dn  PACEd8a86b33            ' \
                           ', \n\r  14   1  23 AN5506-01-A1    A up  FHTT0003ed56            , \n\r  14   1  24 ' \
                           'AN5506-01-A1    A up  FHTT0003ecbd            , \n\r\n\rA: Authorized  P: Preauthorized  ' \
                           'R: System Reserved\n\rAdmin\\gpononu# '
    authorization_list_f = 'show authorization slot 14 link 7\r\n-----  ONU Auth Table ,SLOT=14 PON=7 ,ITEM=3 ' \
                           '-----\n\rSLOT PON ONU     TYPE       ST OST  PHY_ID       PWD       SN LOID, SN ' \
                           'PWD\n\r---- --- --- -------------- -- --- ------------ ---------- ' \
                           '--------------------\n\r  14   7   1 HG260           A up  DGST2140247f            , ' \
                           '\n\r  14   7   2 HG260           A up  PACEd8a779e3            , \n\r  14   7   3 ' \
                           'AN5506-01-A1    A up  FHTT00026010            , \n\r\n\rA: Authorized  P: Preauthorized  ' \
                           'R: System Reserved\n\rAdmin\\gpononu# '

    self.assertEqual(get_last_authorized_number(authorization_list=authorization_list_a), 0)
    self.assertEqual(get_last_authorized_number(authorization_list=authorization_list_b), 4)
    self.assertEqual(get_last_authorized_number(authorization_list=authorization_list_c), 3)
    self.assertEqual(get_last_authorized_number(authorization_list=authorization_list_d), 32)
    self.assertEqual(get_last_authorized_number(authorization_list=authorization_list_e), 15)
    self.assertEqual(get_last_authorized_number(authorization_list=authorization_list_f), 3)
