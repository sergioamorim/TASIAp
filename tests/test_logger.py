from unittest import TestCase

from config import bot_config
from tasiap.logger import get_last_name, get_username, get_logger, log_update
from tests.mock_classes import Message, QueryUpdate, MessageUpdate, PersonInfo


class TestLoggerFunctions(TestCase):

  @classmethod
  def setUpClass(cls):
    cls.first_name_a = 'name a'
    cls.last_name_a = 'surname a'
    cls.username_a = 'nickname a'
    cls.user_id_a = 123456
    cls.callback_query_data_a = 'data a'
    cls.message_text_a = 'text a'

    cls.person_info = PersonInfo(
      first_name=cls.first_name_a,
      last_name=cls.last_name_a,
      username=cls.username_a,
      user_id=cls.user_id_a
    )

    cls.message_from_message_update_a = Message(
      chat=cls.person_info,
      from_user=cls.person_info,
      text=cls.message_text_a,
      from_message=True
    )

    cls.message_from_query_update_a = Message(chat=cls.person_info)

    cls.query_update_a = QueryUpdate(
      message=cls.message_from_query_update_a,
      data=cls.callback_query_data_a
    )

    cls.message_update_a = MessageUpdate(message=cls.message_from_message_update_a)

  def test_get_logger(self):
    logger = get_logger(__name__)

    self.assertTrue(expr=logger.isEnabledFor(level=bot_config.log_level))

    self.assertEqual(
      first=logger.getEffectiveLevel(),
      second=bot_config.log_level
    )

    self.assertTrue(expr=logger.hasHandlers())

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

  def test_log_update(self):

    with self.assertLogs(__name__) as assert_logs:
      def generic_handler(update):
        logger = get_logger(name=__name__)
        log_update(update=update, local_logger=logger)
      generic_handler(update=self.message_update_a)

    expected_output_message_a = [
      'DEBUG:{module_name}:{handler_name} handler: message from '
      '{first_name}{last_name}{username}({user_id}) received: {text}'
      ''.format(
        module_name=__name__,
        handler_name=generic_handler.__name__,
        first_name=self.message_update_a.message.from_user.first_name,

        last_name=get_last_name(
          update=self.message_update_a
        ),

        username=get_username(
          update=self.message_update_a
        ),

        user_id=self.message_update_a.message.from_user.id,
        text=self.message_update_a.message.text
      ),
    ]

    self.assertEqual(first=assert_logs.output, second=expected_output_message_a)

    expected_output_query_a = [
      'DEBUG:{module_name}:{handler_name} handler: message from '
      '{first_name}{last_name}{username}({user_id}) received: {data}'
      ''.format(
        module_name=__name__,
        handler_name=generic_handler.__name__,
        first_name=self.query_update_a.callback_query.message.chat.first_name,

        last_name=get_last_name(
          update=self.query_update_a,
          query=True
        ),

        username=get_username(
          update=self.query_update_a,
          query=True
        ),

        user_id=self.query_update_a.callback_query.message.chat.id,
        data=self.query_update_a.callback_query.data
      ),
    ]

    with self.assertLogs(__name__) as assert_logs:
      def generic_handler(update):
        logger = get_logger(name=__name__)
        log_update(update=update, local_logger=logger)
      generic_handler(update=self.query_update_a)

    self.assertEqual(first=assert_logs.output, second=expected_output_query_a)
