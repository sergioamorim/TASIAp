from tasiap.common.string_common import is_onu_id_valid, onu_address
from tasiap.common.telnet_common import supply_telnet_session, wpa_key, wifi_serv, ssid
from tasiap.logger import get_logger, Log
from tasiap.snmp.onu_wan_service import set_wan_service
from tasiap.snmp.onu_web_admin import set_web_config
from tasiap.snmp.onu_wifi import set_wifi
from tasiap.user_from_onu import find_user_by_onu

logger = get_logger(__name__)


@supply_telnet_session
def get_router_onu_info(onu_id, telnet=None):
  if is_onu_id_valid(onu_id=onu_id):
    current_wifi_serv = wifi_serv(
      onu_address=onu_address(onu_id=onu_id),
      telnet=telnet
    )
    return {
      'onu_id': onu_id,
      'ssid': ssid(current_wifi_serv=current_wifi_serv),
      'wifi_password': wpa_key(current_wifi_serv=current_wifi_serv),
      'username': find_user_by_onu(onu_id=onu_id)
    }
  logger.error(msg='get_router_onu_info: onu id is invalid')
  return None


@Log(logger)
def update_router_onu_config(onu_id, new_ssid=None, wifi_password=None, username=None):
  if is_onu_id_valid(onu_id):
    if username:
      return {'set_web_config': set_web_config(onu_id), 'set_wan_service': set_wan_service(onu_id, username)}
    if new_ssid and wifi_password:
      return set_wifi(onu_id, ssid=new_ssid, wifi_password=wifi_password)
    if new_ssid:
      return set_wifi(onu_id, ssid=new_ssid)
    if wifi_password:
      return set_wifi(onu_id, wifi_password=wifi_password)
  logger.error('update_router_onu_config: onu id is invalid')
  return None
