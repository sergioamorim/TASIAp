from unittest import TestCase
from unittest.mock import patch

from config import bot_config
from tasiap.common.bot_common import is_user_authorized, get_message_from_update, get_signal, get_onu_info_string
from tests.mock_classes import QueryUpdate, MessageUpdate, Message, MockAuthOnuDevice


class TestBotCommonFunctions(TestCase):

  def test_is_user_authorized(self):
    bot_config.permissions = {
      'vlan': [
        '1234567890',
      ],
      'link': [
        '2345678901',
      ],
      'login': [
        '1234567890',
        '2345678901',
      ],
    }

    def vlan(user_id):
      return is_user_authorized(user_id=user_id)

    self.assertTrue(expr=vlan(user_id='1234567890'))
    self.assertFalse(expr=vlan(user_id='2345678901'))

    def link(user_id):
      return is_user_authorized(user_id=user_id)

    self.assertFalse(expr=link(user_id='1234567890'))
    self.assertTrue(expr=link(user_id='2345678901'))

    def login(user_id):
      return is_user_authorized(user_id=user_id)

    self.assertTrue(expr=login(user_id='2345678901'))
    self.assertTrue(expr=login(user_id='1234567890'))

  def test_get_message_from_update(self):
    message_from_callback_query_a = Message()
    message_from_message_update_a = Message(from_message=True)

    self.assertEqual(
      first=get_message_from_update(update=QueryUpdate(message=message_from_callback_query_a)),
      second=message_from_callback_query_a
    )

    self.assertEqual(
      first=get_message_from_update(update=MessageUpdate(message=message_from_message_update_a)),
      second=message_from_message_update_a
    )

  @patch('tasiap.common.bot_common.get_onu_power_signal_by_id')
  def test_get_signal(self, mock_get_onu_power_signal_by_id):
    onu_id = '1234'

    mock_get_onu_power_signal_by_id.return_value = 'not found'
    self.assertEqual(first='não existe ONU autorizada com esse ID.', second=get_signal(onu_id=onu_id))
    mock_get_onu_power_signal_by_id.assert_called_with(onu_id)

    mock_get_onu_power_signal_by_id.return_value = 'off'
    self.assertEqual(first='sem sinal.', second=get_signal(onu_id=onu_id))

    mock_get_onu_power_signal_by_id.return_value = 'error'
    self.assertEqual(first='erro não especificado.', second=get_signal(onu_id=onu_id))

    mock_get_onu_power_signal_by_id.return_value = '-20.00'
    self.assertEqual(first=mock_get_onu_power_signal_by_id.return_value, second=get_signal(onu_id=onu_id))

  @patch(target='tasiap.common.bot_common.find_onu_connection_trigger')
  @patch(target='tasiap.common.bot_common.Thread')
  @patch(target='tasiap.common.bot_common.get_signal')
  @patch(target='tasiap.common.bot_common.signal_job_caller')
  @patch(target='tasiap.common.bot_common.get_auth_onu_device_id')
  def test_get_onu_info_string(
      self,
      mock_get_auth_onu_device_id,
      mock_signal_job_caller,
      mock_get_signal,
      MockThread,
      mock_find_onu_connection_trigger
  ):

    class MockContext:
      bot = 'bot from context'

    context = MockContext()
    update = 'update'
    authorized_onu = MockAuthOnuDevice()

    # test 0: passing authorized_onu without cvlan
    authorized_onu.cvlan = None
    expected_output = 'ID: {onu_id}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=mock_get_auth_onu_device_id.return_value,
      serial=authorized_onu.phy_id,
      signal=mock_signal_job_caller.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, authorized_onu=authorized_onu)
    )
    MockThread.assert_not_called()

    # test 1: passing authorized_onu with cvlan not ending in 00
    authorized_onu.cvlan = '1234'
    expected_output = 'ID: {onu_id}\nCVLAN: {cvlan}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=mock_get_auth_onu_device_id.return_value,
      cvlan=authorized_onu.cvlan,
      serial=authorized_onu.phy_id,
      signal=mock_signal_job_caller.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, authorized_onu=authorized_onu)
    )
    MockThread.assert_not_called()

    # test 2: passing authorized_onu with cvlan 4000
    authorized_onu.cvlan = '4000'
    expected_output = 'ID: {onu_id}\nCVLAN: {cvlan}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=mock_get_auth_onu_device_id.return_value,
      cvlan=authorized_onu.cvlan,
      serial=authorized_onu.phy_id,
      signal=mock_signal_job_caller.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, authorized_onu=authorized_onu)
    )
    MockThread.assert_not_called()

    # test 3: passing onu_id without cvlan
    onu_id = 'onu id'
    serial = 'onu serial'
    expected_output = 'ID: {onu_id}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=onu_id,
      serial=serial,
      signal=mock_get_signal.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, onu_id=onu_id, serial=serial)
    )
    MockThread.assert_not_called()

    # test 4: passing onu_id with cvlan not ending in 00
    onu_id = 'onu id'
    cvlan = '1234'
    serial = 'onu serial'
    expected_output = 'ID: {onu_id}\nCVLAN: {cvlan}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=onu_id,
      cvlan=cvlan,
      serial=serial,
      signal=mock_get_signal.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, onu_id=onu_id, cvlan=cvlan, serial=serial)
    )
    MockThread.assert_not_called()

    # test 5: passing onu_id with cvlan 4000
    onu_id = 'onu id'
    serial = 'onu serial'
    cvlan = '4000'
    expected_output = 'ID: {onu_id}\nCVLAN: {cvlan}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=onu_id,
      cvlan=cvlan,
      serial=serial,
      signal=mock_get_signal.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, onu_id=onu_id, cvlan=cvlan, serial=serial)
    )
    MockThread.assert_not_called()

    # test 6: passing authorized onu with cvlan ending in 00 and it is not 4000
    authorized_onu.cvlan = '1100'
    expected_output = 'ID: {onu_id}\nCVLAN: {cvlan}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=mock_get_auth_onu_device_id.return_value,
      cvlan=authorized_onu.cvlan,
      serial=authorized_onu.phy_id,
      signal=mock_signal_job_caller.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, authorized_onu=authorized_onu)
    )
    MockThread.assert_called_once_with(  # must be the first time with a cvlan and it is not equal to 4000
      target=mock_find_onu_connection_trigger,
      args=(context.bot, update, mock_get_auth_onu_device_id.return_value)
    )

    # test 7: passing onu_id with cvlan ending in 00 and it is not 4000
    onu_id = 'onu id'
    serial = 'onu serial'
    cvlan = '1100'
    expected_output = 'ID: {onu_id}\nCVLAN: {cvlan}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=onu_id,
      cvlan=cvlan,
      serial=serial,
      signal=mock_get_signal.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, onu_id=onu_id, cvlan=cvlan, serial=serial)
    )
    MockThread.assert_called_with(
      target=mock_find_onu_connection_trigger,
      args=(context.bot, update, onu_id)
    )

    # test 7: passing onu_id with signal equals to 'sem sinal.' (without cvlan, but regardless)
    onu_id = 'onu id'
    serial = 'onu serial'
    mock_get_signal.return_value = 'sem sinal.'
    expected_output = 'ID: {onu_id}\nSerial: {serial}\nSinal: {signal}'.format(
      onu_id=onu_id,
      cvlan=cvlan,
      serial=serial,
      signal=mock_signal_job_caller.return_value
    )

    self.assertEqual(
      first=expected_output,
      second=get_onu_info_string(context=context, update=update, onu_id=onu_id, serial=serial)
    )
