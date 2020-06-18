from unittest import TestCase

from config import bot_config
from tasiap.common.bot_common import is_user_authorized, get_message_from_update


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
    class Message:
      chat = None

    class MessageUpdate:
      def __init__(self, message):
        self.message = message

    class CallbackQuery:
      def __init__(self, message):
        self.message = message

    class QueryUpdate:
      def __init__(self, message):
        self.callback_query = CallbackQuery(message=message)

    message_a = Message()

    self.assertEqual(first=get_message_from_update(update=QueryUpdate(message=message_a)), second=message_a)
    self.assertEqual(first=get_message_from_update(update=MessageUpdate(message=message_a)), second=message_a)
