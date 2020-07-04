from unittest import TestCase
from unittest.mock import patch

from tasiap.authorize_onu import format_onu_type, get_last_authorized_number, get_first_missing_number_precedent, \
  get_discovery_list, get_authorization_list, Board, Pon, AuthOnuDevice, find_onu_in_list
from tests.data.authorize_onu_testing_data import authorization_list_tests
from tests.data.telnet_testing_data import test_data
from tests.telnet_testing_environment import TelnetTestingEnvironment


class MockBoard:
  board_id = 12


class MockPon:
  pon_id = 5
  last_authorized_number = 8
  board = MockBoard()


class TestFunctions(TestCase):

  telnet_testing_environment = None

  @classmethod
  def setUpClass(cls):
    cls.telnet_testing_environment = TelnetTestingEnvironment(port=26326)
    cls.telnet_testing_environment.setup()

    cls.expected_generic_response_format = '\r\n{data}\r\nAdmin\\gpononu# '

  @classmethod
  def tearDownClass(cls):
    cls.telnet_testing_environment.tear_down()

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

    expected_response = self.expected_generic_response_format.format(
      data=test_data['default']['discovery']
    )

    self.assertEqual(first=expected_response, second=get_discovery_list())

  def test_get_authorization_list(self):

    expected_response = self.expected_generic_response_format.format(
      data=test_data['default']['authorization']
    )

    self.assertEqual(first=expected_response, second=get_authorization_list(pon=MockPon()))

  def test_find_onu_in_list(self):

    class MockAuthOnuDevice:
      def __init__(self, authorization_id, phy_id):
        self.authorization_id = authorization_id
        self.phy_id = phy_id

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


class TestPon(TestCase):

  @patch(target='tasiap.authorize_onu.get_authorization_list')
  @patch(target='tasiap.authorize_onu.get_last_authorized_number', new=lambda authorization_list: 8)
  def setUp(self, mock_get_last_authorized_number):
    self.last_authorized_number = 8
    self.board_a = MockBoard()
    self.pon_id_a = 6

    self.pon_a = Pon(
      board=self.board_a,
      pon_id=self.pon_id_a,
      tn='telnet connection'
    )

  def test_init(self):
    self.assertEqual(first=self.board_a, second=self.pon_a.board)

  def test_repr(self):
    repr_format = '<Pon(pon_id={pon_id!r},board={board!r},last_authorized_onu_number={last_authorized_onu_number!r})>'
    self.assertEqual(
      first=repr_format.format(
        pon_id=self.pon_id_a,
        board=self.board_a,
        last_authorized_onu_number=self.last_authorized_number
      ),
      second=repr(self.pon_a)
    )


class TestAuthOnuDevice(TestCase):

  def setUp(self):
    self.authorization_id = 1
    self.onu_type = '5506-01-a1'
    self.phy_id = 'PACE0d4cfe07'
    self.pon = MockPon()

    self.onu_device = AuthOnuDevice(
      authorization_id=self.authorization_id,
      onu_type=self.onu_type,
      phy_id=self.phy_id,
      pon=self.pon
    )

  def test_init(self):
    self.assertEqual(first=self.authorization_id, second=self.onu_device.authorization_id)
    self.assertEqual(first=self.onu_type, second=self.onu_device.onu_type)
    self.assertEqual(first=self.phy_id, second=self.onu_device.phy_id)
    self.assertEqual(first=self.pon, second=self.onu_device.pon)

  @patch(target='tasiap.authorize_onu.set_cvlan', side_effect=[None, {'cvlan': 1300}])
  def test_set_cvlan(self, mock_set_cvlan):
    cvlan_a = 1300
    self.onu_device.set_cvlan(cvlan=cvlan_a)
    mock_set_cvlan.assert_called_with(auth_onu_device=self.onu_device, cvlan=cvlan_a)
    self.assertFalse(expr=self.onu_device.cvlan)

    self.onu_device.set_cvlan(cvlan=cvlan_a)
    self.assertEqual(first=cvlan_a, second=self.onu_device.cvlan)

  def test_repr(self):
    repr_format = '' \
      '<AuthOnuDevice(' \
        'phy_id={phy_id!r},' \
        'pon={pon!r},' \
        'onu_type={onu_type!r},' \
        'number={number!r},' \
        'cvlan={cvlan!r},' \
        'authorization_id={authorization_id!r}' \
      ')>' \
      ''

    self.assertEqual(
      first=repr_format.format(
        phy_id=self.onu_device.phy_id,
        pon=self.onu_device.pon,
        onu_type=self.onu_device.onu_type,
        number=self.onu_device.number,
        cvlan=self.onu_device.cvlan,
        authorization_id=self.onu_device.authorization_id
      ),
      second=repr(self.onu_device)
    )
