import unittest
from unittest.mock import patch, MagicMock, call

from tasiap.onu_id_from_username import get_onu_number, get_onu_id_by_mac_and_pon, get_onu_id_by_mac, get_pon_list, \
  format_pon_name, pon_address_from_onu_id, pon_address_from_vlan_name, board_id_and_pon_id_from_vlan_name


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
      obj=get_onu_id_by_mac_and_pon(mac=mac, pon=pon, telnet=telnet),
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
      second=get_onu_id_by_mac_and_pon(mac=mac, pon=pon, telnet=telnet),
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

  @patch(
    target='tasiap.onu_id_from_username.get_pon_list',
    return_value=['slot 12 link 1', 'slot 12 link 2', 'slot 14 link 8']
  )
  @patch(target='tasiap.onu_id_from_username.get_onu_id_by_mac_and_pon')
  def test_get_onu_id_by_mac(self, mock_get_onu_id_by_mac_and_pon, mock_get_pon_list):
    pon_addresses = []
    pon_addresses.extend(mock_get_pon_list.return_value)

    def put_onu_id_in_the_last_pon_available(onu_id):
      mock_get_onu_id_by_mac_and_pon.reset_mock()
      side_effect_of_get_onu_id_by_mac_and_pon = [onu_id]
      side_effect_of_get_onu_id_by_mac_and_pon.extend([None for _ in range(0, len(pon_addresses) - 1)])
      side_effect_of_get_onu_id_by_mac_and_pon.reverse()
      mock_get_onu_id_by_mac_and_pon.side_effect = side_effect_of_get_onu_id_by_mac_and_pon

    telnet = 'telnet connection'
    mac = 'E4:BE:76:54:32:10'

    mock_get_onu_id_by_mac_and_pon.return_value = None
    self.assertIsNone(
      obj=get_onu_id_by_mac(mac=mac, pon=None, telnet=telnet),
      msg='Returns None when the onu_id can not be determined'
    )
    self.assertEqual(
      first=[call(mac, pon_address, telnet=telnet) for pon_address in pon_addresses],
      second=mock_get_onu_id_by_mac_and_pon.mock_calls,
      msg='Checks every pon address available in search for the onu id when no pon is passed'
    )
    self.assertEqual(
      first=[call(telnet=telnet)],
      second=mock_get_pon_list.mock_calls,
      msg='Calls get_pon_list once with the telnet connection passed'
    )

    current_onu_id = '1234'
    put_onu_id_in_the_last_pon_available(onu_id=current_onu_id)
    self.assertEqual(
      first=current_onu_id,
      second=get_onu_id_by_mac(mac=mac, pon=None, telnet=telnet),
      msg='Returns the onu id determined by get_onu_id_by_mac_and_pon when it is found'
    )
    self.assertEqual(
      first=[call(mac, pon_address, telnet=telnet) for pon_address in pon_addresses],
      second=mock_get_onu_id_by_mac_and_pon.mock_calls,
      msg='Checks every pon address available in search for the onu id when no pon is passed'
    )

    put_onu_id_in_the_last_pon_available(onu_id=current_onu_id)
    get_onu_id_by_mac(mac=mac, pon=pon_addresses[0], telnet=telnet)
    self.assertEqual(
      first=[call(mac, pon_address, telnet=telnet) for pon_address in pon_addresses],
      second=mock_get_onu_id_by_mac_and_pon.mock_calls,
      msg=str(
        'Checks every other pon address available in search for the onu id when it can not be found on the pon passed;'
        'Do not check the same pon twice.'
      )
    )

    mock_get_onu_id_by_mac_and_pon.side_effect = None
    mock_get_onu_id_by_mac_and_pon.return_value = current_onu_id
    mock_get_onu_id_by_mac_and_pon.reset_mock()
    get_onu_id_by_mac(mac=mac, pon=pon_addresses[0], telnet=telnet)
    self.assertEqual(
      first=[call(mac, pon_addresses[0], telnet=telnet)],
      second=mock_get_onu_id_by_mac_and_pon.mock_calls,
      msg=str(
        'Calls get_onu_id_by_mac_and_pon only once when the onu id is returned from the pon passed right away'
      )
    )

  @patch(target='tasiap.onu_id_from_username.findall')
  def test_get_pon_list(self, mock_findall):
    telnet = MagicMock()
    pon_pattern = '(slot [0-9]* link [0-9]*) *,auth mode is physical id.'

    self.assertEqual(
      first=mock_findall.return_value,
      second=get_pon_list(telnet=telnet),
      msg='Returns the pon list found with findall'
    )
    self.assertEqual(
      first=[
        call.write(b'cd gponline\n'),
        call.read_until(b'gponline# '),
        call.write(b'show pon_auth all\n'),
        call.read_until(b'Admin\\gponline# '),
        call.read_until().decode('ascii')
      ],
      second=telnet.mock_calls,
      msg=str(
        'Uses the telnet session to enter the directory gponline and uses the command show pon_auth all; reads the '
        'outputs and decodes the last output to ascii.'
      )
    )
    self.assertIn(
      member=[
        call(
          pattern=pon_pattern,
          string=telnet.read_until.return_value.decode.return_value
        )
      ],
      container=mock_findall.mock_calls,
      msg='Calls findall with the pon address pattern and the decoded output gathered from the telnet session.'
    )

  @patch(target='tasiap.onu_id_from_username.get_pon_id')
  @patch(target='tasiap.onu_id_from_username.get_board_id')
  def test_format_pon_name(self, mock_get_board_id, mock_get_pon_id):
    self.assertIsNone(
      obj=format_pon_name(),
      msg='Returns None when neither vlan_name nor onu_id are passed'
    )
    self.assertIsNone(
      obj=format_pon_name(vlan_name='v1200 without explicit board_id or pon_id'),
      msg='Returns None when neither vlan_name nor onu_id are passed'
    )

    onu_id = '1101'
    expected_result = 'slot {board_id} link {pon_id}'.format(
      board_id=mock_get_board_id.return_value,
      pon_id=mock_get_pon_id.return_value
    )
    self.assertEqual(
      first=expected_result,
      second=format_pon_name(onu_id=onu_id),
      msg=str(
        'Returns "slot <board_id> link <pon_id>" from the onu id passed. When the first digit of the onu id passed is '
        '1, the board id is 12. The pon id is the second digit of the onu id passed.'
      )
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_board_id.mock_calls,
      msg='Calls get_board_id with the onu_id passed'
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_pon_id.mock_calls,
      msg='Calls get_pon_id with the onu_id passed'
    )
    self.assertEqual(
      first=expected_result,
      second=format_pon_name(onu_id='2811'),
      msg=str(
        'Returns "slot <board_id> link <pon_id>" from the onu id passed. When the first digit of the onu id passed is '
        '1, the board id is 14. The pon id is the second digit of the onu id passed.'
      )
    )
    self.assertEqual(
      first='slot 12 link 2',
      second=format_pon_name(vlan_name='v4001-P12-PON2'),
      msg=str(
        'Returns "slot <board_id> link <pon_id>" from the vlan name passed when the vlan name format follows the '
        'pattern "<5 characters>-P<board_id>-PON<pon_id>"'
      )
    )
    self.assertEqual(
      first='slot 14 link 7',
      second=format_pon_name(vlan_name='v4002-P14-PON7'),
      msg=str(
        'Returns "slot <board_id> link <pon_id>" from the vlan name passed when the vlan name format follows the '
        'pattern "<5 characters>-P<board_id>-PON<pon_id>"'
      )
    )

  @patch(target='tasiap.onu_id_from_username.get_pon_id')
  @patch(target='tasiap.onu_id_from_username.get_board_id')
  def test_pon_address_from_onu_id(self, mock_get_board_id, mock_get_pon_id):
    onu_id = '1405'
    expected_result = 'slot {board_id} link {pon_id}'.format(
      board_id=mock_get_board_id.return_value,
      pon_id=mock_get_pon_id.return_value
    )
    self.assertEqual(
      first=expected_result,
      second=pon_address_from_onu_id(onu_id=onu_id),
      msg=str(
        'Returns "slot <board_id> link <pon_id>" with board_id being gathered from get_board_id and pon_id from '
        'get_pon_id'
      )
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_board_id.mock_calls,
      msg='Calls get_board_id with the onu_id passed'
    )
    self.assertIn(
      member=[call(onu_id=onu_id)],
      container=mock_get_pon_id.mock_calls,
      msg='Calls get_pon_id with the onu_id passed'
    )

  @patch(target='tasiap.onu_id_from_username.findall')
  def test_board_id_and_pon_id_from_vlan_name(self, mock_findall):
    vlan_name = 'vlan name'
    self.assertEqual(
      first={'board_id': mock_findall.return_value[0][0], 'pon_id': mock_findall.return_value[0][1]},
      second=board_id_and_pon_id_from_vlan_name(vlan_name=vlan_name),
      msg='Returns a dict with the board id and pon id found by findall'
    )
    self.assertIn(
      member=[call(pattern='.*-P([0-9]*)-PON([0-9]*)', string=vlan_name)],
      container=mock_findall.mock_calls,
      msg='Calls findall with the vlan name pattern and the vlan name passed'
    )

    mock_findall.return_value = None
    self.assertIsNone(
      obj=board_id_and_pon_id_from_vlan_name(vlan_name=vlan_name),
      msg='Returns None when vlan name does not match the pattern in findall'
    )

  def test_board_id_and_pon_id_from_vlan_name_integrated_with_findall(self):
    # the goal of this set of tests is to evaluate if the pattern used in findall to catch the board id and pon id is
    # correct
    self.assertEqual(
      first={'board_id': '12', 'pon_id': '1'},
      second=board_id_and_pon_id_from_vlan_name(vlan_name='v1200-P12-PON1-SOMETHING'),
      msg=str(
        'Returns a dict with the board id and pon id found on vlan name with the format '
        '"<something>-P<board_id>-PON<pon_id>"'
      )
    )
    self.assertEqual(
      first={'board_id': '14', 'pon_id': '8'},
      second=board_id_and_pon_id_from_vlan_name(vlan_name='v4025-P14-PON8-SOMETHING'),
      msg=str(
        'Returns a dict with the board id and pon id found on vlan name with the format '
        '"<something>-P<board_id>-PON<pon_id>"'
      )
    )

    self.assertIsNone(
      obj=board_id_and_pon_id_from_vlan_name(vlan_name='v4005 vlan name without explicit board_id or pon_id'),
      msg='Returns None when vlan name does not have explicit board id or pon id'
    )

  @patch(target='tasiap.onu_id_from_username.board_id_and_pon_id_from_vlan_name')
  def test_pon_address_from_vlan_name(self, mock_board_id_and_pon_id_from_vlan_name):
    vlan_name = 'vlan name'

    self.assertEqual(
      first='slot {board_id} link {pon_id}'.format(
        board_id=mock_board_id_and_pon_id_from_vlan_name.return_value['board_id'],
        pon_id=mock_board_id_and_pon_id_from_vlan_name.return_value['pon_id']
      ),
      second=pon_address_from_vlan_name(vlan_name=vlan_name),
      msg=str(
        'Returns "slot <board_id> link <pon_id>" where the board_id and pon_id are extracted from '
        'board_id_and_pon_id_from_vlan_name'
      )
    )
    self.assertIn(
      member=[call(vlan_name=vlan_name)],
      container=mock_board_id_and_pon_id_from_vlan_name.mock_calls,
      msg='Calls board_id_and_pon_id_from_vlan_name with the vlan name passed'
    )

    mock_board_id_and_pon_id_from_vlan_name.return_value = None
    self.assertIsNone(
      obj=pon_address_from_vlan_name(vlan_name=vlan_name),
      msg='Returns None when the board id or pon id can not be found by board_id_and_pon_id_from_vlan_name'
    )
