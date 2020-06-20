class PersonInfo:
  def __init__(self, first_name=None, last_name=None, username=None, user_id=None):
    self.first_name = first_name
    self.last_name = last_name
    self.username = username
    self.id = user_id


class Message:
  def __init__(self, chat=PersonInfo(), data=None, from_user=PersonInfo(), text=None, from_message=False):
    self.chat = chat
    if from_message:
      self.text = text
      self.from_user = from_user
    else:
      self.data = data


class MessageUpdate:
  def __init__(self, message=Message(from_message=True)):
    self.message = message


class CallbackQuery:
  def __init__(self, message=Message(), data=None):
    self.message = message
    self.data = data


class QueryUpdate:
  def __init__(self, message=None):
    self.callback_query = CallbackQuery(message=message)
