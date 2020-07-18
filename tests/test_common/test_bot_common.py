from unittest import TestCase
from unittest.mock import patch

from config import bot_config
from tasiap.common.bot_common import is_user_authorized, get_message_from_update, get_signal
from tests.mock_classes import QueryUpdate, MessageUpdate, Message


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
