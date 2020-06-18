from unittest import TestCase

from tasiap.logger import get_last_name, get_username
from tests.mock_classes import Chat, MessageFromCallbackQuery, MessageFromMessageUpdate, QueryUpdate, MessageUpdate,\
  FromUser


class TestLoggerFunctions(TestCase):

  @classmethod
  def setUpClass(cls):
    cls.first_name_a = 'name a'
    cls.last_name_a = 'surname a'
    cls.username_a = 'nickname a'
    cls.user_id_a = 123456

    cls.chat_a = Chat(
      first_name=cls.first_name_a,
      last_name=cls.last_name_a,
      username=cls.username_a,
      user_id=cls.user_id_a
    )

    cls.from_user_a = FromUser(
      first_name=cls.first_name_a,
      last_name=cls.last_name_a,
      username=cls.username_a,
      user_id=cls.user_id_a
    )

    cls.message_from_message_update_a = MessageFromMessageUpdate(chat=cls.chat_a, from_user=cls.from_user_a)
    cls.message_from_query_update_a = MessageFromCallbackQuery(chat=cls.chat_a)
    cls.query_update_a = QueryUpdate(message=cls.message_from_query_update_a)
    cls.message_update_a = MessageUpdate(message=cls.message_from_message_update_a)

  def test_get_last_name(self):

    self.assertEqual(
      first=get_last_name(update=self.query_update_a, query=True),
      second=' {last_name}'.format(last_name=self.last_name_a)
    )

    self.assertEqual(
      first=get_last_name(update=self.message_update_a),
      second=' {last_name}'.format(last_name=self.last_name_a)
    )

  def test_get_first_name(self):

    self.assertEqual(
      first=get_username(update=self.query_update_a, query=True),
      second=' - @{username} '.format(username=self.username_a)
    )

    self.assertEqual(
      first=get_username(update=self.message_update_a),
      second=' - @{username} '.format(username=self.username_a)
    )
