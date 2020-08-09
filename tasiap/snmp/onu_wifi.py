from tasiap.common.string_common import is_onu_id_valid, int_to_hexoctetstr, string_to_hex_octets, onu_address
from tasiap.common.telnet_common import get_ssid, get_wifi_password
from tasiap.logger import Log, get_logger
from tasiap.snmp.common import snmpset_hex

logger = get_logger(__name__)


def hex_onu_address(current_onu_address):
  return '{hex_board_id} 00 {hex_pon_id} 00 {hex_onu_number}'.format(
    hex_board_id=int_to_hexoctetstr(intvalue=current_onu_address['board_id']),
    hex_pon_id=int_to_hexoctetstr(intvalue=current_onu_address['pon_id']),
    hex_onu_number=int_to_hexoctetstr(intvalue=current_onu_address['onu_number'])
  )


def set_wifi_effective(current_onu_address, ssid, wifi_password):
  hex_string = str(
    '42 47 4D 50 01 00 00 00 00 00 00 AF B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 E1 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 01 E1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 01 00 {hex_onu_address} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 05 00 00 00 04 00 14 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 {ssid_hex} 01 00 00 06 00 04 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 {wifi_password_hex} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
  ).format(
    hex_onu_address=hex_onu_address(current_onu_address=current_onu_address),
    ssid_hex=string_to_hex_octets(string=ssid, length=32),
    wifi_password_hex=string_to_hex_octets(string=wifi_password, length=64)
  )
  if snmpset_hex(snmp_oid='1.3.6.1.4.1.5875.91.1.23.1.1.1.8.1', hex_string=hex_string):
    return {'ssid': ssid, 'wifi_password': wifi_password}
  return None


@Log(logger)
def set_wifi(onu_id, ssid=None, wifi_password=None):
  if is_onu_id_valid(onu_id) and (ssid or wifi_password):
    current_onu_address = onu_address(onu_id=onu_id)
    if not ssid:
      ssid = get_ssid(onu_address=current_onu_address)
    if not wifi_password:
      wifi_password = get_wifi_password(onu_address=current_onu_address)
    return set_wifi_effective(
      current_onu_address=current_onu_address,
      ssid=ssid,
      wifi_password=wifi_password
    )
  logger.error('set_wan_service: invalid onu id or no setting passed')
  return None
