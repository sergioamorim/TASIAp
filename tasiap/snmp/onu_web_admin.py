from config import bot_config
from tasiap.common.string_common import is_onu_id_valid, string_to_hex_octets, onu_address
from tasiap.logger import Log, get_logger
from tasiap.snmp.common import snmpset_hex, hex_onu_address

logger = get_logger(__name__)


def set_web_config_effective(current_onu_address, web_password):
  return snmpset_hex(
    snmp_oid='1.3.6.1.4.1.5875.91.1.22.1.1.1.37.1',
    hex_string=web_config_hex_string(
      current_onu_address=current_onu_address,
      web_password=web_password
    )
  )


@Log(logger)
def set_web_config(onu_id):
  if is_onu_id_valid(onu_id=onu_id):
    return set_web_config_effective(
      current_onu_address=onu_address(onu_id=onu_id),
      web_password=bot_config.default_web_config_password
    )
  logger.error('set_web_config: invalid onu id')
  return None


def web_config_hex_string(current_onu_address, web_password):
  return str(
    '42 47 4D 50 01 00 00 00 00 00 00 61 B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 00 01 00 00 01 3C 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 01 3C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 01 00 {hex_onu_address} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 75 '
    '73 65 72 61 64 6D 69 6E 00 00 00 00 00 00 00 {hex_web_password} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 75 73 65 72 00 00 00 00 00 00 00 00 00 00 00 00 '
    '{hex_web_password} 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 '
    '00 00 00 00 00 61 64 6D 69 6E 00 00 00 00 00 00 00 00 00 00 00 {hex_web_password} 00 00 00 02 00 00 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
  ).format(
    hex_onu_address=hex_onu_address(onu_address=current_onu_address),
    hex_web_password=string_to_hex_octets(string=web_password, length=32)
  )
