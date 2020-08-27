from unittest import TestCase
from unittest.mock import MagicMock, call

from tasiap.onu_id_from_serial import find_onu_by_serial, authorization_table, onu_status_from_phy_id, \
  onu_id_from_address
from tests.data.onu_id_from_serial_testing_data import test_cases


class TestOnuIdFromSerialFunctions(TestCase):

  def test_integrated_find_onu_by_serial(self):
    telnet = MagicMock()

    for test in test_cases:
      telnet.read_until.return_value = test['auth_table']
      for onu in test['onus']:
        self.assertEqual(first=onu['onu_info'], second=find_onu_by_serial(serial=onu['serial'], telnet=telnet))

  def test_authorization_table(self):
    telnet = MagicMock()

    self.assertEqual(
      first=telnet.read_until().decode.return_value,
      second=authorization_table(telnet=telnet),
      msg='Returns the decoded result of the authorization table request'
    )

    self.assertIn(
      member=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'gpononu# '),
        call.write(b'show authorization slot all link all\n'),
        call.read_until(b'gpononu# ')
      ],
      container=telnet.mock_calls,
      msg=str(
        'Requests the authorization table on the gpononu directory from the telnet session passed'
      )
    )
    self.assertIn(
      member=call('ascii'),
      container=telnet.read_until.return_value.decode.mock_calls,
      msg='Decodes the result of the authorization table request from ascii'
    )

    telnet.read_until.return_value = None
    self.assertIsNone(
      obj=authorization_table(telnet=telnet),
      msg='Returns None when the authorization table can not be determined'
    )

  def test_onu_status_from_phy_id(self):
    current_authorization_table = '-----  ONU Auth Table ,SLOT=12 PON=1 ,ITEM=0 -----\n\r'
    phy_id = 'TPLG8edac7ed'
    self.assertIsNone(
      obj=onu_status_from_phy_id(
        current_authorization_table=current_authorization_table,
        phy_id=phy_id
      ),
      msg='Returns None when the authorization table passed has not the authorization tuple for the phy_id passed'
    )

    current_authorization_table = '  12   2   1 HG260           A up  TPLG8edac7ed            , \n\r'
    self.assertEqual(
      first={
        'onu_address': {
          'board_id': '12',
          'pon_id': '2',
          'onu_number': '1'
        },
        'state': 'up'
      },
      second=onu_status_from_phy_id(
        phy_id=phy_id,
        current_authorization_table=current_authorization_table
      ),
      msg=str(
        'Returns the onu address and state of the onu when the authorization tuple for the phy_id passed is found on '
        'the authorization table passed'
      )
    )

  def test_onu_id_from_address(self):
    self.assertEqual(
      first='1101',
      second=onu_id_from_address(onu_address={
        'board_id': '12',
        'pon_id': '1',
        'onu_number': '1'
      })
    )
    self.assertEqual(
      first='1899',
      second=onu_id_from_address(onu_address={
        'board_id': '12',
        'pon_id': '8',
        'onu_number': '99'
      })
    )
    self.assertEqual(
      first='2121',
      second=onu_id_from_address(onu_address={
        'board_id': '14',
        'pon_id': '1',
        'onu_number': '21'
      })
    )
    self.assertEqual(
      first='2202',
      second=onu_id_from_address(onu_address={
        'board_id': '14',
        'pon_id': '2',
        'onu_number': '2'
      })
    )
    self.assertEqual(
      first='2802',
      second=onu_id_from_address(onu_address={
        'board_id': '14',
        'pon_id': '8',
        'onu_number': '2'
      })
    )
