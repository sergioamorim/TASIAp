from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from tasiap.onu_authorization import format_onu_type, get_last_authorized_number, get_first_missing_number_precedent, \
  get_discovery_list, get_authorization_list, Board, Pon, AuthOnuDevice, find_onu_in_list, authorize_onu_effective, \
  get_onu_list, onu_tuples, onu_tuples_found, onus_from_pon_textual, onus_from_pon_textual_found, \
  onus_from_pon_textual_pattern, authorize_onu
from tests.data.onu_authorization_testing_data import authorization_list_tests, discovery_lists_tests
from tests.mock_classes import MockPon, MockAuthOnuDevice, MockBoard


class TestFunctions(TestCase):

  def test_format_onu_type(self):
    onu_type_a = 'AN5506-01-A1'
    onu_type_b = 'AN5506-04-F1'
    onu_type_c = 'HG260'

    self.assertEqual(format_onu_type(onu_type_a), '5506-01-a1')
    self.assertEqual(format_onu_type(onu_type_b), '5506-04-f1')
    self.assertEqual(format_onu_type(onu_type_c), 'hg260')

  def test_get_last_authorized_number(self):
    for test in authorization_list_tests:
      self.assertEqual(
        first=test['last_authorized_number'],
        second=get_last_authorized_number(authorization_list=test['authorization_list'])
      )

  def test_get_first_missing_number_precedent(self):
    tests = [
      {
        'numbers_list': [],
        'first_missing_number_precedent': 0
      },
      {
        'numbers_list': ['1'],
        'first_missing_number_precedent': 1
      },
      {
        'numbers_list': ['1', '3'],
        'first_missing_number_precedent': 1
      },
      {
        'numbers_list': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'first_missing_number_precedent': 9
      },
      {
        'numbers_list': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        'first_missing_number_precedent': 10
      },
      {
        'numbers_list': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11'],
        'first_missing_number_precedent': 9
      },
    ]

    for test in tests:
      self.assertEqual(
        first=test['first_missing_number_precedent'],
        second=get_first_missing_number_precedent(numbers_list=test['numbers_list'])
      )

  def test_get_discovery_list(self):
    telnet = MagicMock()
    self.assertEqual(
      first=telnet.read_until.return_value.decode.return_value,
      second=get_discovery_list(telnet=telnet),
      msg='Returns the decoded discovery list got with the telnet session passed'
    )
    self.assertIn(
      member=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'Admin\\gpononu# '),
        call.write(b'show discovery slot all link all\n'),
        call.read_until(b'Admin\\gpononu# '),
        call.read_until().decode('ascii')
      ],
      container=telnet.mock_calls,
      msg=str(
        'Uses the telnet session passed to enter the gpononu directory and use the show discovery command on all slots '
        'and pons. Reads the output of each command after sending them. Decodes the output of the show discovery '
        'command from ascii after reading it.'
      )
    )

  def test_get_authorization_list(self):
    telnet = MagicMock()
    pon = MockPon()
    self.assertEqual(
      first=telnet.read_until.return_value.decode.return_value,
      second=get_authorization_list(pon=pon, telnet=telnet),
      msg='Returns the decoded authorization list gathered by the telnet session passed.'
    )
    self.assertIn(
      member=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'Admin\\gpononu# '),
        call.write(
          'show authorization slot {board_id} link {pon_id}\n'.format(
            board_id=pon.board.board_id, pon_id=pon.pon_id
          ).encode('ascii')
        ),
        call.read_until(b'Admin\\gpononu# '),
        call.read_until().decode('ascii')
      ],
      container=telnet.mock_calls,
      msg=str(
        'Uses the telnet session passed to enter the gpononu directory, use the show authorization command with the '
        'address of the pon passed and read the output of the commands sent right after sending them. Decodes the '
        'output of the show authorization command from ascii after reading it.'
      )
    )

  def test_find_onu_in_list(self):
    onu_a = MockAuthOnuDevice(authorization_id=1, phy_id='a')
    onu_b = MockAuthOnuDevice(authorization_id=2, phy_id='b')
    onu_list = [onu_a, onu_b]

    self.assertEqual(
      first=onu_a,
      second=find_onu_in_list(onu_list=onu_list, auth_onu=onu_a.authorization_id)
    )
    self.assertEqual(
      first=onu_a,
      second=find_onu_in_list(onu_list=onu_list, auth_onu=onu_a.phy_id)
    )

    self.assertEqual(
      first=onu_b,
      second=find_onu_in_list(onu_list=onu_list, auth_onu=onu_b.authorization_id)
    )
    self.assertEqual(
      first=onu_b,
      second=find_onu_in_list(onu_list=onu_list, auth_onu=onu_b.phy_id)
    )

    self.assertFalse(expr=find_onu_in_list(onu_list=onu_list, auth_onu=-6))
    self.assertFalse(expr=find_onu_in_list(onu_list=onu_list, auth_onu='non existent'))

  @patch(target='tasiap.onu_authorization.update_onu_info')
  def test_authorize_onu_effective(self, mock_update_onu_info):
    onu_a = MockAuthOnuDevice()
    cvlan_a = 2600
    telnet = MagicMock()
    self.assertEqual(
      first=onu_a,
      second=authorize_onu_effective(onu=onu_a, cvlan=cvlan_a, telnet=telnet),
      msg='Returns the onu passed'
    )
    self.assertEqual(
      first=MockAuthOnuDevice.pon.last_authorized_onu_number + 1,
      second=onu_a.number,
      msg="Sets the onu number to one more than it's pon last authorized onu number"
    )
    self.assertEqual(
      first=cvlan_a,
      second=onu_a.cvlan,
      msg='Sets the vlan of the onu to if a non-empty cvlan is passed'
    )
    self.assertEqual(
      first=[call(auth_onu_device=onu_a)],
      second=mock_update_onu_info.mock_calls,
      msg='Pushes the onu into the database'
    )
    self.assertEqual(
      first=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'Admin\\gpononu# '),
        call.write(
          'set whitelist phy_addr address {phy_id} password null action delete\n'.format(
            phy_id=onu_a.phy_id
          ).encode('ascii')
        ),
        call.read_until(b'Admin\\gpononu# '),
        call.write(
          'set authorization slot {board_id} link {pon_id} type {onu_type} onuid {onu_number} phy_id {phy_id}\n'.format(
            board_id=onu_a.pon.board.board_id,
            pon_id=onu_a.pon.pon_id,
            onu_type=onu_a.onu_type,
            onu_number=onu_a.number,
            phy_id=onu_a.phy_id
          ).encode('ascii')
        ),
        call.read_until(b'Admin\\gpononu# '),
        call.write(
          str(
            'set whitelist phy_addr address {phy_id} password null action add slot {board_id} link {pon_id} onu '
            '{onu_number} type {onu_type}\n'
          ).format(
            phy_id=onu_a.phy_id,
            board_id=onu_a.pon.board.board_id,
            pon_id=onu_a.pon.pon_id,
            onu_number=onu_a.number,
            onu_type=onu_a.onu_type
          ).encode('ascii')
        ),
        call.read_until(b'Admin\\gpononu# '),
      ],
      second=telnet.mock_calls,
      msg=str(
        'Uses the telnet session passed to enter the gpononu directory, delete any authorization for the phy_id of the '
        'onu passed that could already exist, authorize the onu passed and then whitelist that same onu. Reads the '
        'output after each command written.'
      )
    )

    onu_b = MockAuthOnuDevice()
    authorize_onu_effective(onu=onu_b, cvlan=None, telnet=telnet)
    self.assertIsNone(obj=onu_b.cvlan, msg='Does not set the onu vlan when no cvlan is passed')

  @patch(target='tasiap.onu_authorization.Pon', new=MockPon)
  @patch(target='tasiap.onu_authorization.AuthOnuDevice', new=MockAuthOnuDevice)
  @patch(target='tasiap.onu_authorization.Board', new=MockBoard)
  def test_get_onu_list(self):
    telnet = 'telnet_connection'

    for test in discovery_lists_tests:
      self.assertEqual(
        first=test['onu_list'],
        second=get_onu_list(discovery_list=test['discovery_list'], telnet=telnet)
      )

  def test_onu_tuples(self):
    for test in discovery_lists_tests:
      for tuples_test in test['onu_tuples_tests']:
        self.assertEqual(
          first=tuples_test['onu_tuples'],
          second=onu_tuples(
            board_id=tuples_test['board_id'],
            discovery_list=test['discovery_list'],
            item_quantity=tuples_test['item_quantity'],
            pon_id=tuples_test['pon_id']
          )
        )

  def test_onu_tuples_found(self):
    for test in discovery_lists_tests:
      for tuples_test in test['onu_tuples_tests']:
        self.assertEqual(
          first=tuples_test['onu_tuples'],
          second=onu_tuples_found(onus_list_textual=tuples_test['onus_list_textual'])
        )

  def test_onus_from_pon_textual(self):
    for test in discovery_lists_tests:
      for tuples_test in test['onu_tuples_tests']:
        self.assertEqual(
          first=tuples_test['onus_list_textual'],
          second=onus_from_pon_textual(
            board_id=tuples_test['board_id'],
            discovery_list=test['discovery_list'],
            item_quantity=tuples_test['item_quantity'],
            pon_id=tuples_test['pon_id']
          )
        )

  def test_onus_from_pon_textual_found(self):
    for test in discovery_lists_tests:
      for tuples_test in test['onu_tuples_tests']:
        self.assertEqual(
          first=tuples_test['onus_list_textual'],
          second=onus_from_pon_textual_found(
            discovery_list=test['discovery_list'],
            pon_discovery_textual_pattern=tuples_test['onus_from_pon_textual_pattern']
          )
        )

  def test_onus_from_pon_textual_pattern(self):
    for test in discovery_lists_tests:
      for tuples_test in test['onu_tuples_tests']:
        self.assertEqual(
          first=tuples_test['onus_from_pon_textual_pattern'],
          second=onus_from_pon_textual_pattern(
            board_id=tuples_test['board_id'],
            item_quantity=tuples_test['item_quantity'],
            pon_id=tuples_test['pon_id']
          )
        )

  @patch(target='tasiap.onu_authorization.get_discovery_list', new=lambda telnet: None)
  @patch(target='tasiap.onu_authorization.authorize_onu_effective', return_value='authorized onu')
  @patch(target='tasiap.onu_authorization.get_onu_list', side_effect=[[], ['onu'], ['onu'], ['onu'], ['onu']])
  @patch(target='tasiap.onu_authorization.find_onu_in_list', side_effect=[None, 'onu found', 'onu found'])
  def test_authorize_onu(self, mock_find_onu_in_list, mock_get_onu_list, mock_authorize_onu_effective):
    telnet = 'telnet_connection'

    self.assertEqual(first=None, second=authorize_onu(telnet=telnet))
    self.assertEqual(first=['onu'], second=authorize_onu(telnet=telnet))

    self.assertEqual(first='ERROR', second=authorize_onu(auth_onu='onu', telnet=telnet))  # 1st call to find_onu_in_list
    self.assertEqual(
      first=mock_authorize_onu_effective.return_value,
      second=authorize_onu(auth_onu='onu', telnet=telnet)
    )
    mock_authorize_onu_effective.assert_called_with(onu='onu found', cvlan=None, telnet=telnet)

    self.assertEqual(
      first=mock_authorize_onu_effective.return_value,
      second=authorize_onu(auth_onu='onu', cvlan='cvlan', telnet=telnet)
    )
    mock_authorize_onu_effective.assert_called_with(onu='onu found', cvlan='cvlan', telnet=telnet)
    mock_find_onu_in_list.assert_called()
    mock_get_onu_list.assert_called()


class TestBoard(TestCase):

  def setUp(self):
    self.board_id_a = 12
    self.board_a = Board(board_id=self.board_id_a)

  def test_init(self):
    self.assertEqual(first=self.board_id_a, second=self.board_a.board_id)

  def test_repr(self):
    repr_format = '<Board(board_id={board_id!r})>'
    self.assertEqual(
      first=repr_format.format(board_id=self.board_id_a),
      second=repr(self.board_a)
    )

  def test_eq(self):
    equal_board = Board(board_id=self.board_id_a)
    not_equal_board = Board(board_id=14)
    self.assertEqual(first=equal_board, second=self.board_a)
    self.assertNotEqual(first=not_equal_board, second=self.board_a)
    self.assertNotEqual(first=None, second=self.board_a)
    self.assertNotEqual(first='string', second=self.board_a)


class TestPon(TestCase):

  @patch(target='tasiap.onu_authorization.get_authorization_list')
  @patch(target='tasiap.onu_authorization.get_last_authorized_number', return_value=MockPon.last_authorized_onu_number)
  def setUp(self, mock_get_last_authorized_number, mock_get_authorization_list):
    self.last_authorized_onu_number = mock_get_last_authorized_number.return_value
    self.board_a = MockBoard()
    self.pon_id_a = 6
    self.telnet = 'telnet connection'

    self.pon_a = Pon(board=self.board_a, pon_id=self.pon_id_a, telnet=self.telnet)
    mock_get_authorization_list.assert_called_once_with(self.pon_a, telnet=self.telnet)

  def test_init(self):
    self.assertEqual(first=self.board_a, second=self.pon_a.board)
    self.assertEqual(first=self.last_authorized_onu_number, second=self.pon_a.last_authorized_onu_number)
    self.assertEqual(first=self.pon_id_a, second=self.pon_a.pon_id)

  def test_repr(self):
    repr_format = '<Pon(pon_id={pon_id!r},board={board!r},last_authorized_onu_number={last_authorized_onu_number!r})>'
    self.assertEqual(
      first=repr_format.format(
        pon_id=self.pon_id_a,
        board=self.board_a,
        last_authorized_onu_number=self.last_authorized_onu_number
      ),
      second=repr(self.pon_a)
    )

  @patch(target='tasiap.onu_authorization.get_authorization_list', return_value='authorization list')
  @patch(target='tasiap.onu_authorization.get_last_authorized_number', return_value=6)
  def test_autoset_last_authorized_number(self, mock_get_last_authorized_number, mock_get_authorization_list):
    telnet = 'telnet_connection'

    self.pon_a.autoset_last_authorized_number(telnet=telnet)
    mock_get_authorization_list.assert_called_once_with(self.pon_a, telnet=telnet)

    mock_get_last_authorized_number.assert_called_once_with(
      authorization_list=mock_get_authorization_list.return_value
    )

    self.assertEqual(
      first=mock_get_last_authorized_number.return_value,
      second=self.pon_a.last_authorized_onu_number
    )

  @patch(target='tasiap.onu_authorization.get_authorization_list')
  @patch(
    target='tasiap.onu_authorization.get_last_authorized_number',
    side_effect=[laon := MockPon.last_authorized_onu_number, laon, laon, laon + 1]
  )
  def test_eq(self, mock_get_last_authorized_number, mock_get_authorization_list):
    assert mock_get_last_authorized_number and mock_get_authorization_list
    equal_pon = Pon(board=self.board_a, pon_id=self.pon_id_a, telnet=self.telnet)

    not_equal_pons = [
      None,
      'some string',
      Pon(board=MockBoard(board_id=14), pon_id=self.pon_id_a, telnet=self.telnet),
      Pon(board=self.board_a, pon_id=self.pon_id_a - 1, telnet=self.telnet),
      Pon(board=self.board_a, pon_id=self.pon_id_a, telnet=self.telnet),
    ]

    self.assertEqual(first=equal_pon, second=self.pon_a)
    for pon in not_equal_pons:
      self.assertNotEqual(first=pon, second=self.pon_a)


class TestAuthOnuDevice(TestCase):

  def setUp(self):
    self.authorization_id = 1
    self.onu_type = '5506-01-a1'
    self.phy_id = 'PACE0d4a1cde'
    self.pon = MockPon()
    self.onu_tuple = ('04', 'AN5506-01-A1', 'DD16b36a1cde')

    self.onu_device_a = AuthOnuDevice(
      authorization_id=self.authorization_id,
      onu_type=self.onu_type,
      phy_id=self.phy_id,
      pon=self.pon
    )

    self.onu_device_b = AuthOnuDevice(
      onu_tuple=self.onu_tuple,
      pon=self.pon
    )

  def test_init(self):
    self.assertEqual(first=self.authorization_id, second=self.onu_device_a.authorization_id)
    self.assertEqual(first=self.onu_type, second=self.onu_device_a.onu_type)
    self.assertEqual(first=self.phy_id, second=self.onu_device_a.phy_id)
    self.assertEqual(first=self.pon, second=self.onu_device_a.pon)

    self.assertEqual(first=str(int(self.onu_tuple[0])), second=self.onu_device_b.authorization_id)
    self.assertEqual(first=format_onu_type(self.onu_tuple[1]), second=self.onu_device_b.onu_type)
    self.assertEqual(first=self.onu_tuple[2], second=self.onu_device_b.phy_id)
    self.assertEqual(first=self.pon, second=self.onu_device_b.pon)

  @patch(target='tasiap.onu_authorization.set_cvlan', side_effect=[None, {'cvlan': 1300}])
  def test_set_cvlan(self, mock_set_cvlan):
    cvlan_a = 1300
    self.onu_device_a.set_cvlan(cvlan=cvlan_a)
    mock_set_cvlan.assert_called_with(auth_onu_device=self.onu_device_a, cvlan=cvlan_a)
    self.assertFalse(expr=self.onu_device_a.cvlan)

    self.onu_device_a.set_cvlan(cvlan=cvlan_a)
    self.assertEqual(first=cvlan_a, second=self.onu_device_a.cvlan)

  def test_repr(self):
    repr_format = str(
      '<AuthOnuDevice('
      'phy_id={phy_id!r},'
      'pon={pon!r},'
      'onu_type={onu_type!r},'
      'number={number!r},'
      'cvlan={cvlan!r},'
      'authorization_id={authorization_id!r}'
      ')>'
    )

    self.assertEqual(
      first=repr_format.format(
        phy_id=self.onu_device_a.phy_id,
        pon=self.onu_device_a.pon,
        onu_type=self.onu_device_a.onu_type,
        number=self.onu_device_a.number,
        cvlan=self.onu_device_a.cvlan,
        authorization_id=self.onu_device_a.authorization_id
      ),
      second=repr(self.onu_device_a)
    )

  def test_eq(self):
    equal_onu_device = AuthOnuDevice(
      authorization_id=self.authorization_id,
      onu_type=self.onu_type,
      phy_id=self.phy_id,
      pon=self.pon
    )

    not_equal_onu_devices = [
      None,
      'string',
      AuthOnuDevice(
        authorization_id=97,
        onu_type=self.onu_type,
        phy_id=self.phy_id,
        pon=self.pon
      ),
      AuthOnuDevice(
        authorization_id=self.authorization_id,
        onu_type='something else',
        phy_id=self.phy_id,
        pon=self.pon
      ),
      AuthOnuDevice(
        authorization_id=self.authorization_id,
        onu_type=self.onu_type,
        phy_id='something else',
        pon=self.pon
      ),
      AuthOnuDevice(
        authorization_id=self.authorization_id,
        onu_type=self.onu_type,
        phy_id=self.phy_id,
        pon=MockPon(pon_id=8)
      ),
    ]

    self.assertEqual(first=equal_onu_device, second=self.onu_device_a)
    for onu_device in not_equal_onu_devices:
      self.assertNotEqual(first=onu_device, second=self.onu_device_a)
