from unittest import TestCase

from config import bot_config
from tasiap.common.bot_common import is_user_authorized, get_message_from_update
from tests.mock_classes import QueryUpdate, MessageUpdate, MessageFromCallbackQuery, MessageFromMessageUpdate


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
    message_from_callback_query_a = MessageFromCallbackQuery()
    message_from_message_update_a = MessageFromMessageUpdate()

    self.assertEqual(
      first=get_message_from_update(update=QueryUpdate(message=message_from_callback_query_a)),
      second=message_from_callback_query_a
    )

    self.assertEqual(
      first=get_message_from_update(update=MessageUpdate(message=message_from_message_update_a)),
      second=message_from_message_update_a
    )
