from tasiap.onu_authorization import Board, Pon, AuthOnuDevice, format_onu_type


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
  def __init__(self, message=None, data=None):
    self.callback_query = CallbackQuery(message=message, data=data)


class MockBoard:
  __eq__ = Board.__eq__
  __repr__ = Board.__repr__

  def __init__(self, board_id=12):
    self.board_id = board_id


class MockPon:
  last_authorized_onu_number = 96
  __eq__ = Pon.__eq__
  __repr__ = Pon.__repr__

  def __init__(self, pon_id=5, board=MockBoard(), board_id=None, tn=None):
    self.pon_id = pon_id
    self.board = Board(board_id=board_id) if board_id else board
    assert tn or not tn


class MockAuthOnuDevice:
  __eq__ = AuthOnuDevice.__eq__
  __repr__ = AuthOnuDevice.__repr__
  cvlan = None
  number = None
  pon = MockPon()

  def __init__(self, authorization_id=3, onu_type='onu_type1', phy_id='ATOZ1a2b0c3f', pon=pon, onu_tuple=None):
    self.authorization_id = str(int(onu_tuple[0])) if onu_tuple else authorization_id
    self.onu_type = format_onu_type(onu_tuple[1]) if onu_tuple else onu_type
    self.phy_id = onu_tuple[2] if onu_tuple else phy_id
    self.pon = pon

  def set_cvlan(self, cvlan):
    self.cvlan = cvlan
