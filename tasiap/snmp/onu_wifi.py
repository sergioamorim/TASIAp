from tasiap.common.string_common import is_onu_id_valid, get_board_id, get_pon_id, get_onu_number_from_id, \
  int_to_hexoctetstr, string_to_hex_octets
from tasiap.common.telnet_common import get_ssid, get_wifi_password
from tasiap.logger import Log, get_logger
from tasiap.snmp.common import snmpset_hex

logger = get_logger(__name__)


def set_wifi_effective(board_id, pon_id, onu_number, ssid, wifi_password):
  hex_string = '42 47 4D 50 01 00 00 00 00 00 00 AF B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 ' \
               '00 01 00 00 01 E1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 E1 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 ' \
               '{board_hex_id} 00 {pon_hex_id} 00 {onu_hex_number} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 ' \
               '05 00 00 00 04 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 01 {ssid_hex} 01 00 00 ' \
               '06 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 {wifi_password_hex} 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00'.format(board_hex_id=int_to_hexoctetstr(board_id),
                                          pon_hex_id=int_to_hexoctetstr(pon_id),
                                          onu_hex_number=int_to_hexoctetstr(onu_number),
                                          ssid_hex=string_to_hex_octets(ssid, 32),
                                          wifi_password_hex=string_to_hex_octets(wifi_password, 64))
  if snmpset_hex(snmp_oid='1.3.6.1.4.1.5875.91.1.23.1.1.1.8.1', hex_string=hex_string):
    return {'ssid': ssid, 'wifi_password': wifi_password}
  return None


@Log(logger)
def set_wifi(onu_id, ssid=None, wifi_password=None):
  if is_onu_id_valid(onu_id) and (ssid or wifi_password):
    board_id = get_board_id(onu_id)
    pon_id = get_pon_id(onu_id)
    onu_number = get_onu_number_from_id(onu_id)
    if not ssid:
      ssid = get_ssid(board_id, pon_id, onu_number)
    if not wifi_password:
      wifi_password = get_wifi_password(board_id, pon_id, onu_number)
    return set_wifi_effective(board_id, pon_id, onu_number, ssid, wifi_password)
  logger.error('set_wan_service: invalid onu id or no setting parsed')
  return None
