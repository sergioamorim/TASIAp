from unittest import TestCase
from unittest.mock import patch, call

from tasiap.manage_router_onu import get_router_onu_info, update_router_onu_config, router_onu_config


class TestManageRouterOnuFunctions(TestCase):

  @patch(target='tasiap.manage_router_onu.wifi_serv')
  @patch(target='tasiap.manage_router_onu.find_user_by_onu')
  @patch(target='tasiap.manage_router_onu.wpa_key')
  @patch(target='tasiap.manage_router_onu.ssid')
  @patch(target='tasiap.manage_router_onu.onu_address')
  @patch(target='tasiap.manage_router_onu.is_onu_id_valid')
  def test_get_router_onu_info(
    self,
    mock_is_onu_id_valid,
    mock_onu_address,
    mock_ssid,
    mock_wpa_key,
    mock_find_user_by_onu,
    mock_wifi_serv
  ):
    telnet = 'telnet'
    onu_id = '1100'
    mock_is_onu_id_valid.return_value = False
    self.assertIsNone(
      obj=get_router_onu_info(onu_id=onu_id, telnet=telnet),
      msg='Returns None when the onu_id is invalid'
    )
    self.assertEqual(
      first=[call(onu_id=onu_id)],
      second=mock_is_onu_id_valid.mock_calls,
      msg='Verifies if the onu_id passed is valid or not'
    )

    mock_is_onu_id_valid.return_value = True
    self.assertEqual(
      first={
        'onu_id': onu_id,
        'ssid': mock_ssid.return_value,
        'wifi_password': mock_wpa_key.return_value,
        'username': mock_find_user_by_onu.return_value
      },
      second=get_router_onu_info(onu_id=onu_id, telnet=telnet),
      msg=str(
        'Returns a dict with the onu_id passed and ssid, wifi_password and username gathered from get_ssid, '
        'get_wifi_password and find_user_by_onu functions respectively '
      )
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_onu_address.mock_calls,
      msg='Gather the onu address from the onu_id passed'
    )
    self.assertIn(
      member=call(current_wifi_serv=mock_wifi_serv.return_value, ),
      container=mock_ssid.mock_calls,
      msg='Reads the ssid from the wifi_serv passed'
    )
    self.assertIn(
      member=call(current_wifi_serv=mock_wifi_serv.return_value),
      container=mock_wpa_key.mock_calls,
      msg='Reads the wifi password from the wifi_serv passed'
    )
    self.assertIn(
      member=call(
        onu_address=mock_onu_address.return_value,
        telnet=telnet
      ),
      container=mock_wifi_serv.mock_calls,
      msg='Gather the wifi_serv from the onu_address gathered and the already open telnet session'
    )
    self.assertEqual(
      first=[call(onu_id=onu_id)],
      second=mock_find_user_by_onu.mock_calls,
      msg='Gather the username from the onu_id passed'
    )

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
      second=update_router_onu_config(onu_id=onu_id, new_ssid=ssid)
    )
    mock_set_wifi.assert_called_with(onu_id, ssid=ssid)

    self.assertEqual(
      first=mock_set_wifi.return_value,
      second=update_router_onu_config(onu_id=onu_id, new_ssid=ssid, wifi_password=wifi_password)
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

  @patch(target='tasiap.manage_router_onu.find_user_by_onu')
  @patch(target='tasiap.manage_router_onu.wpa_key')
  @patch(target='tasiap.manage_router_onu.ssid')
  def test_router_onu_config(self, mock_ssid, mock_wpa_key, mock_find_user_by_onu):
    onu_id = '1234'
    current_wifi_serv = 'wifi serv data string'
    self.assertEqual(
      first={
        'onu_id': onu_id,
        'ssid': mock_ssid.return_value,
        'wifi_password': mock_wpa_key.return_value,
        'username': mock_find_user_by_onu.return_value
      },
      second=router_onu_config(onu_id=onu_id, current_wifi_serv=current_wifi_serv),
      msg='Returns a dict with the onu_id passed and the ssid, wifi_password and username related to that onu'
    )
    self.assertIn(
      member=call(current_wifi_serv=current_wifi_serv),
      container=mock_ssid.mock_calls,
      msg='Gather the ssid from the wifi_serv passed'
    )
    self.assertIn(
      member=call(current_wifi_serv=current_wifi_serv),
      container=mock_wpa_key.mock_calls,
      msg='Gather the wifi_password from the wifi_serv passed'
    )
    self.assertIn(
      member=call(onu_id=onu_id),
      container=mock_find_user_by_onu.mock_calls,
      msg='Gather the username using the onu_id passed'
    )
