from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from config import bot_config
from tasiap.common.bot_common import is_user_authorized, get_message_from_update, get_signal, get_onu_info_string, \
  callback_signal_job, signal_job_caller, find_onu_connection_trigger
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

    self.assertTrue(
      expr=vlan(user_id='1234567890'),
      msg=str(
        "Returns True when the user id passed is in the list of id's on the permissions config for the function called"
      )
    )
    self.assertFalse(
      expr=vlan(user_id='2345678901'),
      msg=str(
        "Returns False when the user id passed is not in the list of id's on the permissions config for the function "
        "called"
      )
    )

    def link(user_id):
      return is_user_authorized(user_id=user_id)

    self.assertFalse(
      expr=link(user_id='1234567890'),
      msg=str(
        "Returns False when the user id passed is not in the list of id's on the permissions config for the function "
        "called"
      )
    )
    self.assertTrue(
      expr=link(user_id='2345678901'),
      msg=str(
        "Returns True when the user id passed is in the list of id's on the permissions config for the function called"
      )
    )

    def login(user_id):
      return is_user_authorized(user_id=user_id)

    self.assertTrue(
      expr=login(user_id='2345678901'),
      msg=str(
        "Returns True when the user id passed is in the list of id's on the permissions config for the function called"
      )
    )
    self.assertTrue(
      expr=login(user_id='1234567890'),
      msg=str(
        "Returns True when the user id passed is in the list of id's on the permissions config for the function called"
      )
    )

  def test_get_message_from_update(self):
    message_from_callback_query_a = Message()
    message_from_message_update_a = Message(from_message=True)

    self.assertEqual(
      first=message_from_callback_query_a,
      second=get_message_from_update(
        update=QueryUpdate(message=message_from_callback_query_a)
      ),
      msg='Returns the message from the callback query when the update refers to a callback carry'
    )

    self.assertEqual(
      first=get_message_from_update(
        update=MessageUpdate(message=message_from_message_update_a)
      ),
      second=message_from_message_update_a,
      msg='Returns the message from the update itself when the update refers to a message'
    )

  @patch('tasiap.common.bot_common.get_onu_power_signal_by_id')
  def test_get_signal(self, mock_get_onu_power_signal_by_id):
    onu_id = '1234'

    mock_get_onu_power_signal_by_id.return_value = 'not found'
    self.assertEqual(
      first='não existe ONU autorizada com esse ID.',
      second=get_signal(onu_id=onu_id),
      msg='Returns the text of non-authorized onu when the onu is not found'
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_get_onu_power_signal_by_id.mock_calls,
      msg='Gather the onu power signal from the onu id passed'
    )

    mock_get_onu_power_signal_by_id.return_value = 'off'
    self.assertEqual(
      first='sem sinal.',
      second=get_signal(onu_id=onu_id),
      msg='Returns the text of onu with no signal when the onu is found off'
    )

    mock_get_onu_power_signal_by_id.return_value = 'error'
    self.assertEqual(
      first='erro não especificado.',
      second=get_signal(onu_id=onu_id),
      msg='Returns a standard error message when an error is encountered in the process of gathering the power signal'
    )

    mock_get_onu_power_signal_by_id.return_value = '-20.00'
    self.assertEqual(
      first=mock_get_onu_power_signal_by_id.return_value,
      second=get_signal(onu_id=onu_id),
      msg='Returns the power signal when it is found'
    )

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
    mock_thread_class,
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
    mock_thread_class.assert_not_called()

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
    mock_thread_class.assert_not_called()

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
    mock_thread_class.assert_not_called()

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
    mock_thread_class.assert_not_called()

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
    mock_thread_class.assert_not_called()

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
    mock_thread_class.assert_not_called()

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
    mock_thread_class.assert_called_once_with(  # must be the first time with a cvlan and it is not equal to 4000
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
    mock_thread_class.assert_called_with(
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

  @patch(target='tasiap.common.bot_common.get_signal')
  def test_callback_signal_job(self, mock_get_signal):
    bot_config.default_chat = '1234567890'
    context = MagicMock()
    context.job.context = {
      'chat_id': int(bot_config.default_chat),
      'onu_id': '1234',
      'message_id': 'message id'
    }

    callback_signal_job(context=context)
    context.bot.send_message.assert_called_once_with(
      context.job.context['chat_id'],
      'Sinal: {signal}'.format(signal=mock_get_signal.return_value),
      reply_to_message_id=context.job.context['message_id']
    )

    context.job.context['chat_id'] += 1
    expected_calls = [
      call(
        int(bot_config.default_chat),
        'ONU ID: {onu_id}\nSinal: {signal}'.format(
          onu_id=context.job.context['onu_id'],
          signal=mock_get_signal.return_value
        )
      ),
      call(
        context.job.context['chat_id'],
        'Sinal: {signal}'.format(signal=mock_get_signal.return_value),
        reply_to_message_id=context.job.context['message_id']
      )
    ]
    callback_signal_job(context=context)
    context.bot.send_message.assert_has_calls(calls=expected_calls, any_order=True)

  @patch(target='tasiap.common.bot_common.get_message_from_update')
  def test_signal_job_caller(self, mock_get_message_from_update):
    context = MagicMock()
    update = 'update'
    onu_id = '1234'

    message = mock_get_message_from_update.return_value
    job_context = {'chat_id': message.chat.id, 'onu_id': onu_id, 'message_id': message.message_id}

    self.assertEqual(
      first='ainda em processo de autorização, o sinal será enviado em 10 segundos.',
      second=signal_job_caller(context=context, update=update, onu_id=onu_id)
    )

    context.job_queue.run_once.assert_called_once_with(callback_signal_job, 10, context=job_context)

  @patch(target='tasiap.common.bot_common.find_onu_connection')
  @patch(target='tasiap.common.bot_common.get_message_from_update')
  def test_find_onu_connection_trigger(self, mock_get_message_from_update, mock_find_onu_connection):
    bot_config.default_chat = '1234567890'
    bot = MagicMock()
    update = 'update'
    onu_id = '1234'
    message = mock_get_message_from_update.return_value
    message.chat.id = int(bot_config.default_chat)
    connection_info = mock_find_onu_connection.return_value
    message_text = str(
      'Roteador conectado na ONU ID {onu_id}.\n'
      'Usuário: {username}\n'
      'Senha: {password}\n'
      'Status da conexão: {status}'
    ).format(
      onu_id=onu_id,
      username=connection_info['username'],
      password=connection_info['password'],
      status=connection_info['diagnostic']
    )

    find_onu_connection_trigger(bot=bot, update=update, onu_id=onu_id)
    bot.send_message.assert_called_once_with(message.chat.id, message_text, reply_to_message_id=message.message_id)

    mock_find_onu_connection.return_value = None
    message_text = 'Nenhum roteador foi conectado na ONU ID {onu_id}.'.format(onu_id=onu_id)
    message.chat.id += 1
    expected_calls = [
      call(message.chat.id, message_text, reply_to_message_id=message.message_id),
      call(int(bot_config.default_chat), message_text)
    ]
    find_onu_connection_trigger(bot=bot, update=update, onu_id=onu_id)
    bot.send_message.assert_has_calls(calls=expected_calls, any_order=True)
