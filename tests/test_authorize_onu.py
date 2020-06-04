from unittest import TestCase, main

from authorize_onu import format_onu_type, get_last_authorized_number


class TestStringFunctions(TestCase):

  def test_format_onu_type(self):
    onu_type_a = 'AN5506-01-A1'
    onu_type_b = 'AN5506-04-F1'
    onu_type_c = 'HG260'

    self.assertEqual(format_onu_type(onu_type_a), '5506-01-a1')
    self.assertEqual(format_onu_type(onu_type_b), '5506-04-f1')
    self.assertEqual(format_onu_type(onu_type_c), 'hg260')

  def test_get_last_authorized_number(self):
    authorization_list = 'show discovery slot all link all\r\n-----  ONU Unauth Table ,SLOT=12 PON=1 ,' \
                         'ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=12 PON=2 ,ITEM=0-----\n\r-----  ONU Unauth ' \
                         'Table ,SLOT=12 PON=3 ,ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=12 PON=4 ,' \
                         'ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=12 PON=5 ,ITEM=0-----\n\r-----  ONU Unauth ' \
                         'Table ,SLOT=12 PON=6 ,ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=12 PON=7 ,' \
                         'ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=12 PON=8 ,ITEM=0-----\n\r-----  ONU Unauth ' \
                         'Table ,SLOT=14 PON=1 ,ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=14 PON=2 ,' \
                         'ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=14 PON=3 ,ITEM=0-----\n\r-----  ONU Unauth ' \
                         'Table ,SLOT=14 PON=4 ,ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=14 PON=5 ,' \
                         'ITEM=3-----\n\rNO       TYPE           PHY_ID        PWD           SN LOID, SN PWD\n\r--  ' \
                         '--------------  ------------  ----------  --------------------------\n\r01  AN5506-01-A1   ' \
                         ' FHTT00026010              , \n\r02  HG260           PACEd8a779e3              , ' \
                         '\n\r03  HG260           DGST2140247f              , \n\r-----  ONU Unauth Table ,' \
                         'SLOT=14 PON=6 ,ITEM=0-----\n\r-----  ONU Unauth Table ,SLOT=14 PON=7 ,ITEM=0-----\n\r----- ' \
                         ' ONU Unauth Table ,SLOT=14 PON=8 ,ITEM=0-----\n\rAdmin\\gpononu# '
    self.assertEqual(get_last_authorized_number(board_id=14, pon_id=5, authorization_list=authorization_list), 0)


if __name__ == '__main__':
  main()
