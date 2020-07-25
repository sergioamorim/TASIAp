from unittest import TestCase
from unittest.mock import patch

from tasiap.manage_router_onu import get_router_onu_info, update_router_onu_config


class TestManageRouterOnuFunctions(TestCase):

  @patch(target='tasiap.manage_router_onu.find_user_by_onu')
  @patch(target='tasiap.manage_router_onu.get_wifi_password')
  @patch(target='tasiap.manage_router_onu.get_ssid')
  @patch(target='tasiap.manage_router_onu.get_onu_number_from_id', new=lambda onu_id: 'not relevant')
  @patch(target='tasiap.manage_router_onu.get_pon_id', new=lambda onu_id: 'not relevant')
  @patch(target='tasiap.manage_router_onu.get_board_id', new=lambda onu_id: 'not relevant')
  @patch(target='tasiap.manage_router_onu.is_onu_id_valid')
  def test_get_router_onu_info(
      self,
      mock_is_onu_id_valid,
      mock_get_ssid,
      mock_get_wifi_password,
      mock_find_user_by_onu
  ):
    telnet = 'telnet'
    onu_id = '1100'
    mock_is_onu_id_valid.return_value = False
    self.assertIsNone(obj=get_router_onu_info(onu_id='110a', tn=telnet))

    mock_is_onu_id_valid.return_value = True
    expected = {
      'onu_id': onu_id,
      'ssid': mock_get_ssid.return_value,
      'wifi_password': mock_get_wifi_password.return_value,
      'username': mock_find_user_by_onu.return_value
    }
    self.assertEqual(first=expected, second=get_router_onu_info(onu_id=onu_id, tn=telnet))

  @patch(target='tasiap.manage_router_onu.set_wifi')
  @patch(target='tasiap.manage_router_onu.set_wan_service')
  @patch(target='tasiap.manage_router_onu.set_web_config')
  @patch(target='tasiap.manage_router_onu.is_onu_id_valid')
  def test_update_router_onu_config(
      self,
      mock_is_onu_id_valid,
      mock_set_web_config,
      mock_set_wan_service,
      mock_set_wifi
  ):
    onu_id = '1100'
    wifi_password = 'pass'
    username = 'user'
    ssid = 'network'

    mock_is_onu_id_valid.return_value = False
    self.assertIsNone(obj=update_router_onu_config(onu_id='110a'))

    mock_is_onu_id_valid.return_value = True
    self.assertIsNone(obj=update_router_onu_config(onu_id=onu_id))

    self.assertEqual(
      first=mock_set_wifi.return_value,
      second=update_router_onu_config(onu_id=onu_id, wifi_password=wifi_password)
    )
    mock_set_wifi.assert_called_once_with(onu_id, wifi_password=wifi_password)

    self.assertEqual(
      first=mock_set_wifi.return_value,
      second=update_router_onu_config(onu_id=onu_id, ssid=ssid)
    )
    mock_set_wifi.assert_called_with(onu_id, ssid=ssid)

    self.assertEqual(
      first=mock_set_wifi.return_value,
      second=update_router_onu_config(onu_id=onu_id, ssid=ssid, wifi_password=wifi_password)
    )
    mock_set_wifi.assert_called_with(onu_id, ssid=ssid, wifi_password=wifi_password)

    expected = {
      'set_web_config': mock_set_web_config.return_value,
      'set_wan_service': mock_set_wan_service.return_value
    }
    self.assertEqual(
      first=expected,
      second=update_router_onu_config(onu_id=onu_id, username=username)
    )
    mock_set_web_config.assert_called_once_with(onu_id)
    mock_set_wan_service.assert_called_once_with(onu_id, username)
