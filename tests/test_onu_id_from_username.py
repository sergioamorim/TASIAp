import unittest
from unittest.mock import patch, MagicMock, call

from tasiap.onu_id_from_username import get_onu_number, get_onu_id_by_mac_and_pon


class TestOutputMethods(unittest.TestCase):

  def test_get_onu_number(self):
    pon_mac_lookup_with_onu_found = str(
      'show pon_mac slot 12 link 1 lookup E4BE76543210\r\n'
      '-----  PON MAC ADDRESS, ITEM=208 -----\n\r'
      '203\tE4:BE:76:54:32:10\t Vid:1100\t OnuId:19\n\r'
      'Admin\\gponline# '
    )
    self.assertEqual(
      first='19',
      second=get_onu_number(pon_mac_lookup_with_onu_found),
      msg='Returns the onu number of a onu found on pon_mac_lookup'
    )

    pon_mac_lookup_without_onu_found = str(
      'show pon_mac slot 12 link 1 lookup A1AAAA11A1A1\r\n'
      '-----  PON MAC ADDRESS, ITEM=208 -----\n\r'
      'Admin\\gponline# '
    )
    self.assertIsNone(
      obj=get_onu_number(pon_mac_lookup_without_onu_found),
      msg='Returns None when there is no onu found in pon_mac_lookup'
    )

  @patch(target='tasiap.onu_id_from_username.get_pon_id')
  @patch(target='tasiap.onu_id_from_username.get_board_id')
  @patch(target='tasiap.onu_id_from_username.get_onu_number')
  def test_get_onu_id_by_mac_and_pon(self, mock_get_onu_number, mock_get_board_id, mock_get_pon_id):
    telnet = MagicMock()
    mac = 'E4:BE:76:54:32:10'
    pon = 'slot 12 link 2'

    mock_get_onu_number.return_value = False
    self.assertIsNone(
      obj=get_onu_id_by_mac_and_pon(mac=mac, pon=pon, tn=telnet),
      msg='Returns None when the onu number can not be determined'
    )
    self.assertEqual(
      first=[
        call.write(b'cd gponline\n'),
        call.read_until(b'Admin\\gponline# ', timeout=1),
        call.write(
          'show pon_mac {pon_address} lookup {mac}\n'.format(pon_address=pon, mac=mac.replace(':', '')).encode('ascii')
        ),
        call.read_until(b'Admin\\gponline# ', timeout=1),
        call.read_until().decode('ascii')
      ],
      second=telnet.mock_calls,
      msg=str(
        'The telnet session is driven to the gponline directory and then the show pon_mac command is executed with the '
        'mac and pon address passed. The buffer is read between the commands. The result of the last reading is '
        'decoded from ASCII.'
      )
    )
    self.assertEqual(
      first=[call(telnet.read_until.return_value.decode.return_value)],
      second=mock_get_onu_number.mock_calls,
      msg=str(
        'Calls get_onu_number function with the pon_mac_lookup decoded data that was gathered from the telnet session '
        'through read_until'
      )
    )

    mock_get_onu_number.return_value = True
    self.assertEqual(
      first='{board_id_single_digit}{pon_id}{leading_zero_of_onu_number}{onu_number}'.format(
        board_id_single_digit=mock_get_board_id.return_value,
        pon_id=mock_get_pon_id.return_value,
        leading_zero_of_onu_number='0' if int(mock_get_onu_number.return_value) < 10 else '',
        onu_number=mock_get_onu_number.return_value
      ),
      second=get_onu_id_by_mac_and_pon(mac=mac, pon=pon, tn=telnet),
      msg=str(
        'Returns the ONU ID is in its compact format when the onu number is found. The single digit board id is '
        'determined by get_board_id and the pon id is determined by get_pon_id. The onu number is the response from '
        'get_onu_number.'
      )
    )
    self.assertIn(
      member=[call(pon_name=pon)],
      container=mock_get_board_id.mock_calls,
      msg='Gather the board id utilising the pon address passed'
    )
    self.assertIn(
      member=[call(pon_name=pon)],
      container=mock_get_pon_id.mock_calls,
      msg='Gather the pon id utilising the pon address passed'
    )
