from tasiap.common.string_common import is_onu_id_valid, onu_address
from tasiap.common.telnet_common import get_wifi_password, get_ssid, supply_telnet_session
from tasiap.logger import get_logger, Log
from tasiap.snmp.onu_wan_service import set_wan_service
from tasiap.snmp.onu_web_admin import set_web_config
from tasiap.snmp.onu_wifi import set_wifi
from tasiap.user_from_onu import find_user_by_onu

logger = get_logger(__name__)


@supply_telnet_session
def get_router_onu_info(onu_id, telnet=None):
  if is_onu_id_valid(onu_id=onu_id):
    current_onu_address = onu_address(onu_id=onu_id)
    return {
      'onu_id': onu_id,
      'ssid': get_ssid(
        onu_address=current_onu_address,
        telnet=telnet
      ),
      'wifi_password': get_wifi_password(
        onu_address=current_onu_address,
        telnet=telnet
      ),
      'username': find_user_by_onu(onu_id=onu_id)
    }
  logger.error(msg='get_router_onu_info: onu id is invalid')
  return None


@Log(logger)
def update_router_onu_config(onu_id, ssid=None, wifi_password=None, username=None):
  if is_onu_id_valid(onu_id):
    if username:
      return {'set_web_config': set_web_config(onu_id), 'set_wan_service': set_wan_service(onu_id, username)}
    if ssid and wifi_password:
      return set_wifi(onu_id, ssid=ssid, wifi_password=wifi_password)
    if ssid:
      return set_wifi(onu_id, ssid=ssid)
    if wifi_password:
      return set_wifi(onu_id, wifi_password=wifi_password)
  logger.error('update_router_onu_config: onu id is invalid')
  return None
