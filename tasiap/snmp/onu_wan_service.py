from tasiap.common.mysql_common import get_login_password
from tasiap.common.string_common import is_onu_id_valid, int_to_hexoctetstr, string_to_hex_octets, \
  assure_two_octet_hexstr, generate_cvlan, onu_address
from tasiap.logger import Log, get_logger
from tasiap.snmp.common import snmpset_hex, hex_onu_address

logger = get_logger(__name__)


def set_wan_service_effective(current_onu_address, vlan_id, username, login_password):
  hex_string = '42 47 4D 50 01 00 00 00 00 00 00 8A B0 A7 0C AE 48 2B 00 00 00 00 00 00 00 00 CC CC CC CC 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 01 00 00 ' \
               '00 01 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 1F 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 ' \
               '{hex_onu_address} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 ' \
               '00 01 49 4E 54 45 52 4E 45 54 5F 52 5F 56 49 44 5F {cvlan_string_hex} 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 01 00 01 {cvlan_hex} 00 00 01 00 02 64 47 7F CC 00 00 00 20 64 7F 00 01 2D A6 38 15 08 08 ' \
               '08 08 00 {username_hex} {login_password_hex} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0F 0F 01 00 FF FF FF FF 00 81 00 FF FF FF FF 00 ' \
               '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'.format(
    hex_onu_address=hex_onu_address(onu_address=current_onu_address),
    cvlan_string_hex=string_to_hex_octets(vlan_id, 4),
    cvlan_hex=assure_two_octet_hexstr(int_to_hexoctetstr(int(vlan_id))),
    username_hex=string_to_hex_octets(username, 32),
    login_password_hex=string_to_hex_octets(login_password, 32))
  if snmpset_hex(snmp_oid='1.3.6.1.4.1.5875.91.1.8.1.1.1.13.1', hex_string=hex_string):
    return {'cvlan': vlan_id, 'username': username, 'password': login_password}
  return None


@Log(logger)
def set_wan_service(onu_id, username):
  if is_onu_id_valid(onu_id=onu_id):
    current_onu_address = onu_address(onu_id=onu_id)
    return set_wan_service_effective(
      current_onu_address=current_onu_address,
      vlan_id=generate_cvlan(
        board_id=current_onu_address['board_id'],
        pon_id=current_onu_address['pon_id']
      ),
      username=username,
      login_password=get_login_password(username=username)
    )
  logger.error('set_wan_service: invalid onu id')
  return None
