from unittest import TestCase
from unittest.mock import MagicMock, call

from tasiap.onu_restart import restart_onu, restart_onu_effective


class TestOnuRestartFunctions(TestCase):

  def test_restart_onu(self):
    telnet = MagicMock()
    current_onu_address = {
      'board_id': '12',
      'pon_id': '1',
      'onu_number': '1'
    }

    telnet.read_until.return_value = b'no onu satisfy the list'
    self.assertEqual(
      first='not found',
      second=restart_onu(current_onu_address=current_onu_address, telnet=telnet),
      msg="Returns 'not found' when the onu specified is not found"
    )
    self.assertIn(
      member=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'gpononu# '),
        call.write('reset slot {board_id} link {pon_id} onulist {onu_number}\n'.format(
          board_id=current_onu_address['board_id'],
          pon_id=current_onu_address['pon_id'],
          onu_number=current_onu_address['onu_number']
        ).encode('ascii')),
        call.read_until(b'gpononu# ')
      ],
      container=telnet.mock_calls,
      msg=''
    )

    telnet.read_until.return_value = b'reset onu ok'
    self.assertEqual(
      first='done',
      second=restart_onu(current_onu_address=current_onu_address, telnet=telnet),
      msg="Returns 'done' when the command to restart the onu is successfully sent"
    )

    telnet.read_until.return_value = b'some unexpected or unknown result'
    self.assertEqual(
      first='error',
      second=restart_onu(current_onu_address=current_onu_address, telnet=telnet),
      msg="Returns 'error' when an unexpected result is encountered"
    )

    telnet.read_until.return_value = None
    self.assertIsNone(
      obj=restart_onu(current_onu_address=current_onu_address, telnet=telnet),
      msg='Returns None when the telnet session does not respond'
    )

  def test_restart_onu_effective(self):
    telnet = MagicMock()
    current_onu_address = {
      'board_id': '12',
      'pon_id': '1',
      'onu_number': '1'
    }
    telnet.read_until.return_value = None
    self.assertIsNone(
      obj=restart_onu_effective(current_onu_address=current_onu_address, telnet=telnet),
      msg='Returns None when the telnet session does not respond to the restart command'
    )
    self.assertIn(
      member=[
        call.write(b'cd gpononu\n'),
        call.read_until(b'gpononu# '),
        call.write(
          'reset slot {board_id} link {pon_id} onulist {onu_number}\n'
          ''.format(
            board_id=current_onu_address['board_id'],
            pon_id=current_onu_address['pon_id'],
            onu_number=current_onu_address['onu_number']
          ).encode('ascii')
        ),
        call.read_until(b'gpononu# ')
      ],
      container=telnet.mock_calls,
      msg='Requests the onu restart on the gpononu directory from the telnet session passed'
    )
    self.assertNotIn(
      member=call.read_until().decode('ascii'),
      container=telnet.mock_calls,
      msg='Does not try to decode a result when the result is None'
    )

    telnet.read_until.return_value = MagicMock()
    self.assertEqual(
      first=telnet.read_until.return_value.decode.return_value,
      second=restart_onu_effective(current_onu_address=current_onu_address, telnet=telnet),
      msg='Returns the result of the restart command decoded if any'
    )
    self.assertIn(
      member=call.read_until().decode('ascii'),
      container=telnet.mock_calls,
      msg='Decodes the result of the restart from ascii command if any'
    )
