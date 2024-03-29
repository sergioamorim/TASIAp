from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, call

from tasiap.common.string_common import get_auth_onu_device_id, sanitize_cto_vlan_name, format_strhexoctet, \
  hexstr_to_hexoctetstr, int_to_hexoctetstr, assure_two_octet_hexstr, get_onu_number_from_id, get_pon_id, \
  str_char_to_hex_octet, string_to_hex_octets, generate_cvlan, get_board_id, is_onu_id_valid, is_vlan_id_valid, \
  is_serial_valid, remove_accents, sanitize_dumb, is_int, get_caller_name, get_onu_id_from_cto_vlan_name, \
  get_cto_name_from_cto_vlan_name, get_vlan_id_from_cto_vlan_name, get_vlan_type, format_datetime, format_onu_state, \
  get_enable_emoji, get_status_emoji, sanitize_name, is_query_update, format_clients_message, \
  is_string_addition_too_big, get_client_info_message_block, onu_address
from tasiap.onu_authorization import AuthOnuDevice, Pon, Board
from tests.mock_classes import MessageUpdate, QueryUpdate


class TestStringFunctions(TestCase):

  @patch(target='tasiap.common.string_common.get_onu_number_from_id')
  @patch(target='tasiap.common.string_common.get_pon_id')
  @patch(target='tasiap.common.string_common.get_board_id')
  def test_onu_address(self, mock_get_board_id, mock_get_pon_id, mock_get_onu_number_from_id):
    onu_id = '1234'
    self.assertEqual(
      first={
        'board_id': mock_get_board_id.return_value,
        'pon_id': mock_get_pon_id.return_value,
        'onu_number': mock_get_onu_number_from_id.return_value
      },
      second=onu_address(onu_id=onu_id),
      msg='Returns a dict with board_id, pon_id and onu_number from the onu_id passed'
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_get_board_id.mock_calls,
      msg='The board_id is gathered from the onu_id passed'
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_get_board_id.mock_calls,
      msg='The pon_id is gathered from the onu_id passed'
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_get_board_id.mock_calls,
      msg='The onu_number is gathered from the onu_id passed'
    )

  def test_get_auth_onu_device_id(self):
    def mock_init_pon(pon, pon_id, board):
      pon.pon_id = pon_id
      pon.board = board

    with patch.object(Pon, '__init__', mock_init_pon):
      board_a = Board('14')
      pon_a = Pon(pon_id='1', board=board_a)
      onu_a = AuthOnuDevice(authorization_id='1', onu_type='AN5506-04-F1', phy_id='FHTT1177bc38', pon=pon_a)
      onu_a.number = 4

      board_b = Board('12')
      pon_b = Pon(pon_id='1', board=board_b)
      onu_b = AuthOnuDevice(authorization_id='1', onu_type='AN5506-04-F1', phy_id='FHTT1177bc38', pon=pon_b)
      onu_b.number = 1

      board_c = Board('14')
      pon_c = Pon(pon_id='8', board=board_c)
      onu_c = AuthOnuDevice(authorization_id='1', onu_type='AN5506-04-F1', phy_id='FHTT1177bc38', pon=pon_c)
      onu_c.number = 99
      self.assertEqual(get_auth_onu_device_id(onu_a), '2104')
      self.assertEqual(get_auth_onu_device_id(onu_b), '1101')
      self.assertEqual(get_auth_onu_device_id(onu_c), '2899')

  def test_sanitize_cto_vlan_name(self):
    vlan_a = 'v1101-P12-PON1-ONU01-CTO-PPPOE-MERC-SANTANA'
    vlan_a_sanitized = 'CTO 1101 MERC SANTANA'

    vlan_b = 'v1100-P12-PON1-CLIENTES-FIBRA'

    vlan_c = 'v1135-P12-PON1-ONU35-CTO-PPPOE-MERCADINHO-POPULAR'
    vlan_c_sanitized = 'CTO 1135 MERCADINHO POPULAR'

    vlan_d = 'v4000-PPPOE-TEMPORARIO'

    vlan_e = 'v2806-P14-PON8-ONU06-P2P-PPPOE-TONY'
    vlan_e_sanitized = 'P2P 2806 TONY'

    vlan_f = 'v2115-P14-PON1-ONU15-CTO-PPPOE-SOBS'
    vlan_f_sanitized = 'CTO 2115 SOBS'

    vlan_g = 'v1116-P12-PON5-ONU36-CTO-PPPOE-ACOUGUE-GSS'
    vlan_g_sanitized = 'CTO 1536 (v1116) ACOUGUE GSS'

    vlan_h = 'v1303-P12-PON6-ONU02-CTO-PPPOE-KIDUCHA'
    vlan_h_sanitized = 'CTO 1602 (v1303) KIDUCHA'

    vlan_i = 'REDE-PPPOE-ESCRITORIO'

    self.assertEqual(first=sanitize_cto_vlan_name(vlan_a), second=vlan_a_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_c), second=vlan_c_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_e), second=vlan_e_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_f), second=vlan_f_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_g), second=vlan_g_sanitized)
    self.assertEqual(first=sanitize_cto_vlan_name(vlan_h), second=vlan_h_sanitized)

    self.assertFalse(expr=sanitize_cto_vlan_name(vlan_b))
    self.assertFalse(expr=sanitize_cto_vlan_name(vlan_d))
    self.assertFalse(expr=sanitize_cto_vlan_name(vlan_i))

  def test_format_strhexoctet(self):
    self.assertEqual(first=format_strhexoctet(strhexoctet=''), second='00')
    self.assertEqual(first=format_strhexoctet(strhexoctet='a'), second='0A')
    self.assertEqual(first=format_strhexoctet(strhexoctet='af'), second='AF')

  def test_hexstr_to_hexoctetstr(self):
    self.assertEqual(first=hexstr_to_hexoctetstr(hexstr=''), second='00')
    self.assertEqual(first=hexstr_to_hexoctetstr(hexstr='a'), second='0A')
    self.assertEqual(first=hexstr_to_hexoctetstr(hexstr='af'), second='AF')
    self.assertEqual(first=hexstr_to_hexoctetstr(hexstr='af1'), second='0A F1')
    self.assertEqual(first=hexstr_to_hexoctetstr(hexstr='af10000000b'), second='0A F1 00 00 00 0B')

  def test_int_to_hexoctetstr(self):
    self.assertEqual(first=int_to_hexoctetstr(intvalue=0), second='00')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=9), second='09')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=10), second='0A')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=15), second='0F')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=16), second='10')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=31), second='1F')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=32), second='20')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=255), second='FF')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=256), second='01 00')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=4095), second='0F FF')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=4096), second='10 00')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=65535), second='FF FF')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=65535), second='FF FF')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=65536), second='01 00 00')
    self.assertEqual(first=int_to_hexoctetstr(intvalue=281474976710656), second='01 00 00 00 00 00 00')

  def test_assure_two_octet_hexstr(self):
    self.assertEqual(first=assure_two_octet_hexstr(hexstr='00'), second='00 00')
    self.assertEqual(first=assure_two_octet_hexstr(hexstr='FF'), second='00 FF')
    self.assertEqual(first=assure_two_octet_hexstr(hexstr='FF FF'), second='FF FF')
    self.assertEqual(first=assure_two_octet_hexstr(hexstr='00 FF'), second='00 FF')
    self.assertEqual(first=assure_two_octet_hexstr(hexstr='10 00'), second='10 00')

  def test_get_onu_number_from_id(self):
    self.assertEqual(first=get_onu_number_from_id(onu_id='1234'), second=34)
    self.assertEqual(first=get_onu_number_from_id(onu_id='1299'), second=99)
    self.assertEqual(first=get_onu_number_from_id(onu_id='1201'), second=1)

  def test_get_pon_id(self):
    self.assertFalse(expr=get_pon_id())
    self.assertEqual(first=get_pon_id(onu_id='1234'), second='2')
    self.assertEqual(first=get_pon_id(pon_name='slot 12 link 8'), second='8')

  def test_str_char_to_hex_octect(self):
    self.assertEqual(first=str_char_to_hex_octet(str_char='a'), second='61')
    self.assertEqual(first=str_char_to_hex_octet(str_char='\\'), second='5C')
    self.assertEqual(first=str_char_to_hex_octet(str_char='6'), second='36')

  def test_string_to_hex_octects(self):
    self.assertEqual(first=string_to_hex_octets(string='', length=0), second='')
    self.assertEqual(first=string_to_hex_octets(string='', length=1), second='00')
    self.assertEqual(first=string_to_hex_octets(string='', length=13), second='00 00 00 00 00 00 00 00 00 00 00 00 00')
    self.assertEqual(first=string_to_hex_octets(string='a', length=12), second='61 00 00 00 00 00 00 00 00 00 00 00')
    self.assertEqual(first=string_to_hex_octets(string='abcdef', length=11), second='61 62 63 64 65 66 00 00 00 00 00')
    self.assertEqual(first=string_to_hex_octets(string='0abcdef', length=10), second='30 61 62 63 64 65 66 00 00 00')
    self.assertEqual(first=string_to_hex_octets(string='0abcdef', length=10), second='30 61 62 63 64 65 66 00 00 00')
    self.assertEqual(first=string_to_hex_octets(string='"0abcd\'f\\', length=9), second='22 30 61 62 63 64 27 66 5C')

  def test_generate_cvlan(self):
    self.assertEqual(first=generate_cvlan(board_id='12', pon_id='1'), second='1100')
    self.assertEqual(first=generate_cvlan(board_id='12', pon_id='8'), second='1800')
    self.assertEqual(first=generate_cvlan(board_id='14', pon_id='1'), second='2100')
    self.assertEqual(first=generate_cvlan(board_id='14', pon_id='8'), second='2800')

  def test_get_board_id(self):
    self.assertFalse(expr=get_board_id())
    self.assertEqual(first=get_board_id(onu_id='1234'), second='12')
    self.assertEqual(first=get_board_id(onu_id='2345'), second='14')
    self.assertEqual(first=get_board_id(pon_name='slot 12 link 1'), second='1')
    self.assertEqual(first=get_board_id(pon_name='slot 14 link 1'), second='2')

  def test_is_onu_id_valid(self):
    self.assertFalse(expr=is_onu_id_valid(onu_id='1100'))
    self.assertFalse(expr=is_onu_id_valid(onu_id=''))
    self.assertFalse(expr=is_onu_id_valid(onu_id='0'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='1'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='10'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='99'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='100'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='999'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='123'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='a'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='abcd'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='ab01'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='a101'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='103a'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='1030'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='0130'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='5130'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='5130'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='4130'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='3900'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='3901'))
    self.assertFalse(expr=is_onu_id_valid(onu_id='1012'))

    self.assertTrue(expr=is_onu_id_valid(onu_id='1101'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='1199'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='1899'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='1801'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='2101'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='2199'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='2801'))
    self.assertTrue(expr=is_onu_id_valid(onu_id='2899'))

  def test_is_vlan_id_valid(self):
    self.assertFalse(expr=is_vlan_id_valid(vlan_id=''))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id=0))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id='0'))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id=4086))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id='4086'))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id='a200'))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id='120a'))
    self.assertFalse(expr=is_vlan_id_valid(vlan_id='1a00'))

    self.assertTrue(expr=is_vlan_id_valid(vlan_id=1))
    self.assertTrue(expr=is_vlan_id_valid(vlan_id='1'))
    self.assertTrue(expr=is_vlan_id_valid(vlan_id=4085))
    self.assertTrue(expr=is_vlan_id_valid(vlan_id='4085'))

  def test_is_serial_valid(self):
    self.assertFalse(expr=is_serial_valid(serial=''))
    self.assertFalse(expr=is_serial_valid(serial='6a0b1c2d3e4f5'))
    self.assertFalse(expr=is_serial_valid(serial='abcd12345678'))
    self.assertFalse(expr=is_serial_valid(serial='ABCD12345g78'))
    self.assertFalse(expr=is_serial_valid(serial='ABCD12345G78'))
    self.assertFalse(expr=is_serial_valid(serial='ZzYW121Ff6780'))

    self.assertTrue(expr=is_serial_valid(serial='ABCD12345678'))
    self.assertTrue(expr=is_serial_valid(serial='ABCD121Ff6780'))
    self.assertTrue(expr=is_serial_valid(serial='ZZYW121Ff67a0'))

  def test_remove_accents(self):
    self.assertEqual(first=remove_accents(string=''), second='')
    self.assertEqual(first=remove_accents(string='a'), second='a')
    self.assertEqual(first=remove_accents(string='0a1vz9fZP[\' "'), second='0a1vz9fZP[\' "')
    self.assertEqual(first=remove_accents(string='áàâãÁÀÂÃéêÉÊíÍóôõÓÔÕúÚ'), second='aaaaAAAAeeEEiIoooOOOuU')
    self.assertEqual(first=remove_accents(string='0Ffáàâã\'ÁÀÂÃéêma3ÉÊíÍ óôõÓÔ"ÕúÚzA'),
                     second='0Ffaaaa\'AAAAeema3EEiI oooOO"OuUzA')

  def test_sanitize_dumb(self):
    self.assertEqual(first=sanitize_dumb(string=''), second='')
    self.assertEqual(first=sanitize_dumb(string='a'), second='a')
    self.assertEqual(first=sanitize_dumb(string='0a1vz9fZP[\' "'), second='0a1vz9fZP[\' "')
    self.assertEqual(first=sanitize_dumb(string='0a1vz9fZP[\'  "'), second='0a1vz9fZP[\' "')
    self.assertEqual(first=sanitize_dumb(string='0a1vz9fZP[\'  ",'), second='0a1vz9fZP[\' ", ')
    self.assertEqual(first=sanitize_dumb(string='0a1vz9fZP[\'  ",'), second='0a1vz9fZP[\' ", ')
    self.assertEqual(first=sanitize_dumb(string='0a1vz9fZP[\'  ",// /\t , / '), second='0a1vz9fZP[\' ",, ,, ')

  def test_is_int(self):
    self.assertFalse(expr=is_int(s=''))
    self.assertFalse(expr=is_int(s='a'))
    self.assertFalse(expr=is_int(s='a1'))
    self.assertFalse(expr=is_int(s='1a1'))
    self.assertFalse(expr=is_int(s='1a'))
    self.assertFalse(expr=is_int(s='aa'))

    self.assertTrue(expr=is_int(s=0))
    self.assertTrue(expr=is_int(s='0'))
    self.assertTrue(expr=is_int(s=1))
    self.assertTrue(expr=is_int(s='1'))
    self.assertTrue(expr=is_int(s=281474976710656))
    self.assertTrue(expr=is_int(s='281474976710656'))

  def test_get_caller_name(self):
    self.assertEqual(first=get_caller_name(), second='_callTestMethod')

    def generic_function_label():
      return get_caller_name()

    self.assertEqual(first=generic_function_label(), second='test_get_caller_name')

  def test_get_onu_id_from_cto_vlan_name(self):
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v1101-P12-PON1-ONU01-CTO-PPPOE-MERC-SANTANA'),
                     second='1101')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v1108-P12-PON1-ONU08-CTO-PPPOE-IML'),
                     second='1108')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v1319-P12-PON3-ONU19-CTO-PPPOE-NAIR'),
                     second='1319')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v1806-P12-PON8-ONU06-CTO-PPPOE-ESQUINA-DIVINO'),
                     second='1806')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v1116-P12-PON5-ONU36-CTO-PPPOE-ACOUGE-GSS'),
                     second='1536')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v1303-P12-PON6-ONU02-CTO-PPPOE-KIDUCHA'),
                     second='1602')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v2101-P14-PON1-ONU01-CTO-PPPOE-IGREJA-MORMONS'),
                     second='2101')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v2115-P14-PON1-ONU15-CTO-PPPOE-SOBS'),
                     second='2115')
    self.assertEqual(first=get_onu_id_from_cto_vlan_name(cto_vlan_name='v2806-P14-PON8-ONU06-P2P-PPPOE-TONY'),
                     second='2806')

  def test_get_cto_name_from_cto_vlan_name(self):
    self.assertEqual(first=get_cto_name_from_cto_vlan_name(cto_vlan_name=''), second='')
    self.assertEqual(first=get_cto_name_from_cto_vlan_name(cto_vlan_name='a'), second='')
    self.assertEqual(first=get_cto_name_from_cto_vlan_name(cto_vlan_name='v1108-P12-PON1-ONU08-CTO-PPPOE-IML'),
                     second='IML')
    self.assertEqual(first=get_cto_name_from_cto_vlan_name(cto_vlan_name='v2806-P14-PON8-ONU06-P2P-PPPOE-TONY'),
                     second='TONY')
    self.assertEqual(first=get_cto_name_from_cto_vlan_name(
      cto_vlan_name='v1506-P12-PON6-ONU05-CTO-PPPOE-FARM-TRAB-AV-BELMIRO-AMORIM-ST-LUCIA'),
      second='FARM TRAB AV BELMIRO AMORIM ST LUCIA')

  def test_get_vlan_id_from_cto_vlan_name(self):
    self.assertEqual(first=get_vlan_id_from_cto_vlan_name(cto_vlan_name='v1108-P12-PON1-ONU08-CTO-PPPOE-IML'),
                     second='1108')

  def test_get_vlan_type(self):
    self.assertEqual(first=get_vlan_type(vlan_name='v1108-P12-PON1-ONU08-CTO-PPPOE-IML'), second='CTO')
    self.assertEqual(first=get_vlan_type(vlan_name='v2806-P14-PON8-ONU06-P2P-PPPOE-TONY'), second='P2P')

  def test_format_datetime(self):
    datetime_object = datetime(2020, 6, 8, 18, 34, 42, 14936)
    self.assertEqual(first=format_datetime(datetime_object=datetime_object),
                     second='08/06/2020 18:34:42')
    self.assertEqual(first=format_datetime(datetime_object=datetime_object, safename=True),
                     second='2020-06-08_18-34-42')
    self.assertEqual(first=format_datetime(datetime_object=datetime_object, readable=True),
                     second='18:34:42 de 08/06/2020')

  def test_format_onu_state(self):
    self.assertEqual(first=format_onu_state(onu_state='up'), second='online')
    self.assertEqual(first=format_onu_state(onu_state='down'), second='offline')
    self.assertEqual(first=format_onu_state(onu_state='dw'), second='offline')

  def test_get_enable_emoji(self):
    self.assertEqual(first=get_enable_emoji(enable=True), second='✅')
    self.assertEqual(first=get_enable_emoji(enable=False), second='❌')

  def test_get_status_emoji(self):
    self.assertEqual(first=get_status_emoji(status=0), second='🚫')
    self.assertEqual(first=get_status_emoji(status=1), second='🔹')
    self.assertEqual(first=get_status_emoji(status=2), second='💲')
    self.assertEqual(first=get_status_emoji(status=3), second='🔴')
    self.assertEqual(first=get_status_emoji(status=5), second='🔴')

  def test_sanitize_name(self):
    self.assertEqual(first=sanitize_name(name='name surname'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='* NAME SUrNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='** NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='**NAME surname'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='*name SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='0-NAMe SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='0-name surname'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='1 - NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='1 -NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='1-**NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='1-*NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='1-NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='F *NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='F* NAME SURNAME'), second='NAME SURNAME')
    self.assertEqual(first=sanitize_name(name='F*NAME SURNAME'), second='NAME SURNAME')

  def test_is_query_update(self):
    self.assertFalse(expr=is_query_update(update=MessageUpdate()))
    self.assertTrue(expr=is_query_update(update=QueryUpdate()))

  def test_get_client_info_message_block(self):
    search_name = 'NAME SURNAME A'
    client_a = {'nome': search_name, 'endereco': 'address a', 'numero': '6a', 'complemento': '', 'referencia': '',
                'observacao': '', 'status': 1, 'user': 'username a', 'pass': '', 'enable': 1, 'groupname': 'plan a'}
    result_a = '🔹 Nome: <u>NAME SURNAME A</u>\nEndereço: address a, 6a\nPlano: plan a\n✅ <b>Usuário:</b> ' \
               '<code>username a</code>\n'
    client_b = {'nome': search_name, 'endereco': 'address b', 'numero': '6b',
                'complemento': 'bb' + search_name,
                'referencia': search_name + 'b',
                'observacao': 'b' + search_name,
                'status': 1, 'user': 'username b', 'pass': '', 'enable': 1,
                'groupname': 'plan b'}
    result_b = '🔹 Nome: <u>NAME SURNAME A</u>\nEndereço: address b, 6b\nComplemento: bbNAME SURNAME ' \
               'A\nReferencia: NAME SURNAME Ab\nObservacao: bNAME SURNAME A\nPlano: plan b\n✅ <b>Usuário:</b> ' \
               '<code>username b</code>\n'
    self.assertEqual(first=get_client_info_message_block(client=client_a), second=result_a)
    self.assertEqual(first=get_client_info_message_block(client=client_a, search_name=search_name), second=result_a)
    self.assertEqual(first=get_client_info_message_block(client=client_b, search_name=search_name), second=result_b)

  def test_is_string_addition_too_big(self):
    self.assertFalse(expr=is_string_addition_too_big(string='a', string_addition='b', character_limit=21))
    self.assertTrue(expr=is_string_addition_too_big(string='c', string_addition='d', character_limit=20))

  def test_format_clients_message(self):
    name_a = 'NAME SURNAME A'
    result_a = {'direct': [{'nome': 'NAME SURNAME A', 'endereco': 'address a', 'numero': '6a', 'complemento': '',
                            'referencia': '', 'observacao': '', 'status': 1, 'user': 'username a', 'pass': '',
                            'enable': 1, 'groupname': 'plan a'}], 'related': []}
    message_a = '🔹 Nome: <u>NAME SURNAME A</u>\nEndereço: address a, 6a\nPlano: plan a\n✅ ' \
                '<b>Usuário:</b> <code>username a</code>\n'
    self.assertEqual(first=format_clients_message(name=name_a, result=result_a), second=message_a)

    result_b = {'direct': [], 'related': []}
    message_b = 'Nenhum cliente encontrado com o termo informado.'
    self.assertEqual(first=format_clients_message(name=None, result=result_b), second=message_b)

    name = 'NAME SURNAME'
    username = 'username{id}'
    set_size = 39
    clients_list = [{'nome': '{name} {id}'.format(name=name, id=i), 'endereco': 'address', 'numero': '6a',
                     'complemento': '', 'referencia': '', 'observacao': '', 'status': 1, 'user': username.format(id=i),
                     'pass': '', 'enable': 1, 'groupname': 'plan'} for i in range(0, set_size)]

    message = ''
    for i in range(0, set_size - 1):
      message += '🔹 Nome: <u>{name} {id}</u>\nEndereço: address, 6a\nPlano: plan\n✅ <b>Usuário:</b> ' \
                 '<code>username{id}</code>\n'.format(name=name, id=i)
    message += '\n\n<b>CROPPED!</b>'

    result_direct = {'direct': clients_list, 'related': []}
    self.assertEqual(first=format_clients_message(name=name, result=result_direct), second=message)

    result_related = {'direct': [], 'related': clients_list}
    self.assertEqual(first=format_clients_message(name=name, result=result_related), second=message)
