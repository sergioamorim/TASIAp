from unittest import TestCase

from tasiap.user_from_onu import get_mac_list
from tests.data.telnet_testing_data import show_pon_mac


class TestOutputMethods(TestCase):

  def test_get_mac_list(self):
    for onu_number in show_pon_mac['macs_from_onu'].keys():
      self.assertEqual(
        first=get_mac_list(show_pon_mac=show_pon_mac['data'], onu_number=onu_number),
        second=show_pon_mac['macs_from_onu'][onu_number],
        msg='Returns the list of macs linked to the given onu number on the show_pon_mac output passed'
      )
