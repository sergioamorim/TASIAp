class PersonInfo:
  def __init__(self, first_name=None, last_name=None, username=None, user_id=None):
    self.first_name = first_name
    self.last_name = last_name
    self.username = username
    self.id = user_id


class Chat(PersonInfo):
  pass


class FromUser(PersonInfo):
  pass


class HasChat:
  def __init__(self, chat=Chat()):
    self.chat = chat


class MessageFromMessageUpdate(HasChat):
  def __init__(self, chat=None, from_user=FromUser(), text=None):
    self.from_user = from_user
    self.text = text
    super().__init__(chat=chat)


class MessageFromCallbackQuery(HasChat):
  pass


class MessageUpdate:
  def __init__(self, message=MessageFromMessageUpdate()):
    self.message = message


class CallbackQuery:
  def __init__(self, message=MessageFromCallbackQuery(), data=None):
    self.message = message
    self.data = data


class QueryUpdate:
  def __init__(self, message=None):
    self.callback_query = CallbackQuery(message=message)
