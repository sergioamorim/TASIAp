from unittest import TestCase, main

from user_from_onu import get_mac_list


class TestOutputMethods(TestCase):

  def test_get_mac_list(self):

    show_pon_mac = b'show pon_mac slot 12 link 1\r\n-----  PON MAC ADDRESS, ITEM=203 ' \
                   b'-----\n\r001\t00:1A:3F:86:EC:0A\t Vid:1100\t OnuId:26\n\r002\t00:1A:3F:E8:45:28\t Vid:1100\t ' \
                   b'OnuId:10\n\r003\t00:E0:4C:9B:92:83\t Vid:1100\t OnuId:18\n\r004\t04:8D:38:0C:7B:F7\t Vid:1100\t ' \
                   b'OnuId:14\n\r005\t18:0F:76:7F:57:E9\t Vid:1100\t OnuId:38\n\r006\t18:D6:C7:5D:40:FB\t Vid:1100\t ' \
                   b'OnuId:27\n\r007\t18:D6:C7:79:38:4D\t Vid:1100\t OnuId:11\n\r008\t38:6B:1C:0B:DA:F9\t Vid:1100\t ' \
                   b'OnuId:29\n\r009\t50:0F:F5:5D:9F:00\t Vid:1100\t OnuId:21\n\r010\t58:10:8C:5A:B5:4F\t Vid:1100\t ' \
                   b'OnuId:37\n\r011\t58:10:8C:91:97:FC\t Vid:1100\t OnuId:23\n\r012\t78:44:76:82:09:6B\t Vid:1100\t ' \
                   b'OnuId:34\n\r013\tB0:4E:26:3C:E5:F7\t Vid:1100\t OnuId:36\n\r014\tB0:4E:26:9C:40:59\t Vid:1100\t ' \
                   b'OnuId:40\n\r015\tC4:12:F5:D3:31:93\t Vid:1100\t OnuId:31\n\r016\tC8:3A:35:33:FE:C8\t Vid:1100\t ' \
                   b'OnuId:13\n\r017\tC8:3A:35:46:12:70\t Vid:1100\t OnuId:28\n\r018\tC8:E7:D8:9E:1B:21\t Vid:1100\t ' \
                   b'OnuId:12\n\r019\tC8:E7:D8:AC:C8:79\t Vid:1100\t OnuId:22\n\r020\tC8:E7:D8:AD:E7:45\t Vid:1100\t ' \
                   b'OnuId:20\n\r021\tCC:06:77:69:DC:B3\t Vid:1100\t OnuId:33\n\r022\tD8:FE:E3:73:CF:55\t Vid:1100\t ' \
                   b'OnuId:17\n\r023\tE4:BE:ED:1B:C0:E1\t Vid:1100\t OnuId:32\n\r024\tE4:BE:ED:5F:E1:89\t Vid:1100\t ' \
                   b'OnuId:39\n\r025\tE4:BE:ED:9B:26:9F\t Vid:1100\t OnuId:7\n\r026\tE4:BE:ED:A2:2E:7E\t Vid:1100\t ' \
                   b'OnuId:25\n\r027\tE8:65:D4:38:80:58\t Vid:1100\t OnuId:30\n\r028\t58:10:8C:26:DC:30\t Vid:1101\t ' \
                   b'OnuId:1\n\r029\t58:10:8C:46:8D:67\t Vid:1101\t OnuId:1\n\r030\t58:10:8C:B0:E9:8E\t Vid:1101\t ' \
                   b'OnuId:1\n\r031\t78:44:76:8F:BB:07\t Vid:1101\t OnuId:1\n\r032\t78:44:76:90:65:0F\t Vid:1101\t ' \
                   b'OnuId:1\n\r033\t78:44:76:90:C1:27\t Vid:1101\t OnuId:1\n\r034\tC4:6E:1F:AC:76:27\t Vid:1101\t ' \
                   b'OnuId:1\n\r035\tC8:3A:35:7C:FE:30\t Vid:1101\t OnuId:1\n\r036\tE4:BE:ED:1B:64:1B\t Vid:1101\t ' \
                   b'OnuId:1\n\r037\tEC:08:6B:88:74:F3\t Vid:1101\t OnuId:1\n\r038\t00:1A:3F:7D:15:C8\t Vid:1102\t ' \
                   b'OnuId:2\n\r039\t00:1A:3F:FA:B1:10\t Vid:1102\t OnuId:2\n\r040\t04:8D:39:4F:44:7A\t Vid:1102\t ' \
                   b'OnuId:2\n\r041\t14:CC:20:B7:96:6B\t Vid:1102\t OnuId:2\n\r042\t18:D6:C7:26:3A:29\t Vid:1102\t ' \
                   b'OnuId:2\n\r043\t3C:8C:F8:80:9D:4D\t Vid:1102\t OnuId:2\n\r044\t58:10:8C:94:36:9E\t Vid:1102\t ' \
                   b'OnuId:2\n\r045\t78:44:76:90:5D:47\t Vid:1102\t OnuId:2\n\r046\tB0:4E:26:7D:57:13\t Vid:1102\t ' \
                   b'OnuId:2\n\r047\tC4:6E:1F:91:73:11\t Vid:1102\t OnuId:2\n\r048\tC8:3A:35:D7:50:C0\t Vid:1102\t ' \
                   b'OnuId:2\n\r049\tC8:E7:D8:87:84:59\t Vid:1102\t OnuId:2\n\r050\tE4:BE:ED:1E:1E:54\t Vid:1102\t ' \
                   b'OnuId:2\n\r051\t00:72:63:0E:9D:6B\t Vid:1103\t OnuId:3\n\r052\t00:E0:4C:9B:13:1F\t Vid:1103\t ' \
                   b'OnuId:3\n\r053\t00:E0:4C:9B:EE:6F\t Vid:1103\t OnuId:3\n\r054\t6C:72:20:4E:2F:03\t Vid:1103\t ' \
                   b'OnuId:3\n\r055\t78:44:76:90:35:C7\t Vid:1103\t OnuId:3\n\r056\t78:44:76:90:CC:FB\t Vid:1103\t ' \
                   b'OnuId:3\n\r057\tC8:3A:35:00:6B:10\t Vid:1103\t OnuId:3\n\r058\tC8:3A:35:6E:76:18\t Vid:1103\t ' \
                   b'OnuId:3\n\r059\tC8:3A:35:C8:A6:A8\t Vid:1103\t OnuId:3\n\r060\tE4:BE:ED:30:7B:AC\t Vid:1103\t ' \
                   b'OnuId:3\n\r061\t00:1A:3F:24:F3:A2\t Vid:1104\t OnuId:4\n\r062\t00:1A:3F:85:D2:23\t Vid:1104\t ' \
                   b'OnuId:4\n\r063\t00:1A:3F:AA:AB:1C\t Vid:1104\t OnuId:4\n\r064\t00:1A:3F:C0:B3:E7\t Vid:1104\t ' \
                   b'OnuId:4\n\r065\t00:72:63:0A:C0:70\t Vid:1104\t OnuId:4\n\r066\t0C:B6:D2:83:94:E0\t Vid:1104\t ' \
                   b'OnuId:4\n\r067\t38:6B:1C:10:B6:5B\t Vid:1104\t OnuId:4\n\r068\t58:10:8C:6B:62:07\t Vid:1104\t ' \
                   b'OnuId:4\n\r069\tC8:3A:35:02:8E:48\t Vid:1104\t OnuId:4\n\r070\t00:1A:3F:1F:9D:F1\t Vid:1105\t ' \
                   b'OnuId:5\n\r071\t00:1A:3F:94:E2:D6\t Vid:1105\t OnuId:5\n\r072\t00:1A:3F:BF:AE:59\t Vid:1105\t ' \
                   b'OnuId:5\n\r073\t00:1A:3F:C1:88:29\t Vid:1105\t OnuId:5\n\r074\t00:1A:3F:DE:2F:84\t Vid:1105\t ' \
                   b'OnuId:5\n\r075\t00:1A:3F:E8:45:36\t Vid:1105\t OnuId:5\n\r076\t00:1A:3F:E9:52:2C\t Vid:1105\t ' \
                   b'OnuId:5\n\r077\t00:72:63:13:8F:0D\t Vid:1105\t OnuId:5\n\r078\t00:E0:4B:F8:9C:6D\t Vid:1105\t ' \
                   b'OnuId:5\n\r079\t00:E0:4B:F8:EF:5D\t Vid:1105\t OnuId:5\n\r080\t00:E0:4C:64:F8:9F\t Vid:1105\t ' \
                   b'OnuId:5\n\r081\t00:E0:4C:9B:86:4B\t Vid:1105\t OnuId:5\n\r082\t04:8D:38:0C:86:92\t Vid:1105\t ' \
                   b'OnuId:5\n\r083\t18:0D:2C:9B:1E:B5\t Vid:1105\t OnuId:5\n\r084\t18:A6:F7:8F:BE:79\t Vid:1105\t ' \
                   b'OnuId:5\n\r085\t3C:E5:B4:09:78:DB\t Vid:1105\t OnuId:5\n\r086\t50:0F:F5:01:11:70\t Vid:1105\t ' \
                   b'OnuId:5\n\r087\t58:10:8C:2F:75:36\t Vid:1105\t OnuId:5\n\r088\t58:10:8C:BC:C4:73\t Vid:1105\t ' \
                   b'OnuId:5\n\r089\t78:44:76:90:C0:CB\t Vid:1105\t OnuId:5\n\r090\tAC:84:C6:47:74:85\t Vid:1105\t ' \
                   b'OnuId:5\n\r091\tD4:6E:0E:FA:03:F3\t Vid:1105\t OnuId:5\n\r092\tD8:0D:17:45:B1:D7\t Vid:1105\t ' \
                   b'OnuId:5\n\r093\tD8:32:14:34:86:30\t Vid:1105\t OnuId:5\n\r094\tE4:BE:ED:32:B3:EA\t Vid:1105\t ' \
                   b'OnuId:5\n\r095\tE4:BE:ED:92:F2:FD\t Vid:1105\t OnuId:5\n\r096\tE4:BE:ED:A1:F5:44\t Vid:1105\t ' \
                   b'OnuId:5\n\r097\tE8:DE:27:6B:E1:41\t Vid:1105\t OnuId:5\n\r098\tE8:DE:27:95:7F:15\t Vid:1105\t ' \
                   b'OnuId:5\n\r099\tF4:F2:6D:AF:5E:3B\t Vid:1105\t OnuId:5\n\r100\t00:1A:3F:8E:8A:3F\t Vid:1106\t ' \
                   b'OnuId:6\n\r101\t00:1A:3F:DB:E7:EB\t Vid:1106\t OnuId:6\n\r102\t00:1A:3F:E5:1C:D4\t Vid:1106\t ' \
                   b'OnuId:6\n\r103\t00:1A:3F:FD:A5:5C\t Vid:1106\t OnuId:6\n\r104\t00:72:63:08:31:5B\t Vid:1106\t ' \
                   b'OnuId:6\n\r105\t00:72:63:0B:D8:7E\t Vid:1106\t OnuId:6\n\r106\t00:E0:4C:0F:3D:4F\t Vid:1106\t ' \
                   b'OnuId:6\n\r107\t00:E0:4C:1D:EE:4B\t Vid:1106\t OnuId:6\n\r108\t00:E0:4C:9B:7F:73\t Vid:1106\t ' \
                   b'OnuId:6\n\r109\t14:CC:20:E9:97:B1\t Vid:1106\t OnuId:6\n\r110\t18:0D:2C:55:8B:F0\t Vid:1106\t ' \
                   b'OnuId:6\n\r111\t20:AA:4B:DB:80:11\t Vid:1106\t OnuId:6\n\r112\t28:3B:82:75:3F:8D\t Vid:1106\t ' \
                   b'OnuId:6\n\r113\t58:10:8C:6B:30:9F\t Vid:1106\t OnuId:6\n\r114\t70:62:B8:7E:BD:19\t Vid:1106\t ' \
                   b'OnuId:6\n\r115\t78:44:76:90:A8:6F\t Vid:1106\t OnuId:6\n\r116\t90:94:E4:D1:D1:25\t Vid:1106\t ' \
                   b'OnuId:6\n\r117\tA0:AB:1B:19:29:7C\t Vid:1106\t OnuId:6\n\r118\tBC:4C:C4:41:FA:A2\t Vid:1106\t ' \
                   b'OnuId:6\n\r119\tC0:4A:00:0A:6E:91\t Vid:1106\t OnuId:6\n\r120\tC8:E7:D8:6A:EE:4F\t Vid:1106\t ' \
                   b'OnuId:6\n\r121\tC8:E7:D8:AC:D8:5B\t Vid:1106\t OnuId:6\n\r122\tCC:2D:21:3C:23:48\t Vid:1106\t ' \
                   b'OnuId:6\n\r123\tD4:6E:0E:FA:00:B3\t Vid:1106\t OnuId:6\n\r124\tE4:BE:ED:60:23:8D\t Vid:1106\t ' \
                   b'OnuId:6\n\r125\t00:1A:3F:18:1A:BF\t Vid:1108\t OnuId:8\n\r126\t00:1A:3F:C2:B1:79\t Vid:1108\t ' \
                   b'OnuId:8\n\r127\t00:1A:3F:D1:2E:1B\t Vid:1108\t OnuId:8\n\r128\t04:8D:38:EC:84:5C\t Vid:1108\t ' \
                   b'OnuId:8\n\r129\t04:8D:39:4F:6C:2A\t Vid:1108\t OnuId:8\n\r130\t0C:80:63:CE:C5:97\t Vid:1108\t ' \
                   b'OnuId:8\n\r131\t10:FE:ED:6F:8C:73\t Vid:1108\t OnuId:8\n\r132\t24:FD:0D:63:4B:88\t Vid:1108\t ' \
                   b'OnuId:8\n\r133\t38:6B:1C:0F:28:9F\t Vid:1108\t OnuId:8\n\r134\t58:10:8C:53:51:E1\t Vid:1108\t ' \
                   b'OnuId:8\n\r135\t70:4F:57:E0:50:E7\t Vid:1108\t OnuId:8\n\r136\t78:44:76:71:91:8F\t Vid:1108\t ' \
                   b'OnuId:8\n\r137\t78:44:76:82:00:7F\t Vid:1108\t OnuId:8\n\r138\t98:DE:D0:B8:06:EF\t Vid:1108\t ' \
                   b'OnuId:8\n\r139\t98:FC:11:C0:19:25\t Vid:1108\t OnuId:8\n\r140\tC8:3A:35:29:61:28\t Vid:1108\t ' \
                   b'OnuId:8\n\r141\tC8:3A:35:34:98:F8\t Vid:1108\t OnuId:8\n\r142\tC8:3A:35:35:CB:40\t Vid:1108\t ' \
                   b'OnuId:8\n\r143\tC8:3A:35:49:2F:80\t Vid:1108\t OnuId:8\n\r144\tC8:3A:35:DD:9A:30\t Vid:1108\t ' \
                   b'OnuId:8\n\r145\tE4:BE:ED:6C:41:43\t Vid:1108\t OnuId:8\n\r146\tE4:BE:ED:7C:F8:8F\t Vid:1108\t ' \
                   b'OnuId:8\n\r147\tE4:BE:ED:B4:27:94\t Vid:1108\t OnuId:8\n\r148\tE4:BE:ED:E4:1C:AE\t Vid:1108\t ' \
                   b'OnuId:8\n\r149\t00:1A:3F:29:11:79\t Vid:1109\t OnuId:9\n\r150\t00:1A:3F:9C:8A:C5\t Vid:1109\t ' \
                   b'OnuId:9\n\r151\t00:1A:3F:C1:62:55\t Vid:1109\t OnuId:9\n\r152\t00:1A:3F:F0:40:2E\t Vid:1109\t ' \
                   b'OnuId:9\n\r153\t00:72:63:08:D8:E0\t Vid:1109\t OnuId:9\n\r154\t00:72:63:09:1E:F4\t Vid:1109\t ' \
                   b'OnuId:9\n\r155\t00:72:63:13:94:59\t Vid:1109\t OnuId:9\n\r156\t38:6B:1C:12:C6:01\t Vid:1109\t ' \
                   b'OnuId:9\n\r157\t58:10:8C:20:27:A1\t Vid:1109\t OnuId:9\n\r158\t58:10:8C:2D:1D:A6\t Vid:1109\t ' \
                   b'OnuId:9\n\r159\t58:10:8C:3A:B6:38\t Vid:1109\t OnuId:9\n\r160\t58:10:8C:A9:F3:42\t Vid:1109\t ' \
                   b'OnuId:9\n\r161\t6C:72:20:4D:EA:33\t Vid:1109\t OnuId:9\n\r162\t6C:72:20:4D:F4:91\t Vid:1109\t ' \
                   b'OnuId:9\n\r163\t78:44:76:70:EF:7F\t Vid:1109\t OnuId:9\n\r164\t78:44:76:71:26:3F\t Vid:1109\t ' \
                   b'OnuId:9\n\r165\t78:44:76:90:84:C7\t Vid:1109\t OnuId:9\n\r166\tB8:55:10:54:DF:8D\t Vid:1109\t ' \
                   b'OnuId:9\n\r167\tC0:4A:00:C4:C9:19\t Vid:1109\t OnuId:9\n\r168\tC8:3A:35:24:C9:A8\t Vid:1109\t ' \
                   b'OnuId:9\n\r169\tC8:3A:35:33:CA:50\t Vid:1109\t OnuId:9\n\r170\tC8:3A:35:45:5C:48\t Vid:1109\t ' \
                   b'OnuId:9\n\r171\tC8:3A:35:5A:D1:38\t Vid:1109\t OnuId:9\n\r172\tE4:BE:ED:5F:E4:59\t Vid:1109\t ' \
                   b'OnuId:9\n\r173\tE4:BE:ED:A1:DD:2F\t Vid:1109\t OnuId:9\n\r174\tE4:BE:ED:A2:12:C7\t Vid:1109\t ' \
                   b'OnuId:9\n\r175\t30:B5:C2:7B:9B:AB\t Vid:1115\t OnuId:15\n\r176\t54:E6:FC:A1:8F:39\t Vid:1115\t ' \
                   b'OnuId:15\n\r177\t58:10:8C:2B:86:98\t Vid:1115\t OnuId:15\n\r178\tC8:3A:35:A1:D6:A0\t Vid:1115\t ' \
                   b'OnuId:15\n\r179\t00:1A:3F:D0:DA:B9\t Vid:1119\t OnuId:19\n\r180\t00:72:63:13:96:E4\t Vid:1119\t ' \
                   b'OnuId:19\n\r181\t00:E0:20:4E:5B:E7\t Vid:1119\t OnuId:19\n\r182\t00:E0:4C:5D:80:0B\t Vid:1119\t ' \
                   b'OnuId:19\n\r183\t0C:80:63:89:23:07\t Vid:1119\t OnuId:19\n\r184\t14:CC:20:E9:98:1F\t Vid:1119\t ' \
                   b'OnuId:19\n\r185\t18:0D:2C:C0:B4:E5\t Vid:1119\t OnuId:19\n\r186\t58:10:8C:16:15:58\t Vid:1119\t ' \
                   b'OnuId:19\n\r187\t58:10:8C:C1:AA:9E\t Vid:1119\t OnuId:19\n\r188\t58:10:8C:C1:F7:02\t Vid:1119\t ' \
                   b'OnuId:19\n\r189\t64:66:B3:BB:C2:0D\t Vid:1119\t OnuId:19\n\r190\t68:FF:7B:5D:FE:B1\t Vid:1119\t ' \
                   b'OnuId:19\n\r191\t70:4F:57:3E:F5:81\t Vid:1119\t OnuId:19\n\r192\t78:44:76:90:BE:43\t Vid:1119\t ' \
                   b'OnuId:19\n\r193\t98:DA:C4:B7:F0:E6\t Vid:1119\t OnuId:19\n\r194\tC8:3A:35:3F:61:B8\t Vid:1119\t ' \
                   b'OnuId:19\n\r195\tC8:3A:35:DE:87:28\t Vid:1119\t OnuId:19\n\r196\tC8:E7:D8:75:73:03\t Vid:1119\t ' \
                   b'OnuId:19\n\r197\tE4:BE:ED:1D:68:A6\t Vid:1119\t OnuId:19\n\r198\tE4:BE:ED:22:E4:F3\t Vid:1119\t ' \
                   b'OnuId:19\n\r199\tE4:BE:ED:30:88:22\t Vid:1119\t OnuId:19\n\r200\tE4:BE:ED:8F:91:9E\t Vid:1119\t ' \
                   b'OnuId:19\n\r201\tC8:3A:35:32:0C:E8\t Vid:1135\t OnuId:35\n\r202\tCC:06:77:69:DC:B1\t Vid:4087\t ' \
                   b'OnuId:33\n\r203\t22:3E:44:55:66:11\t Vid:4091\t OnuId:65535\n\rAdmin\\gponline# '.decode('ascii')

    expected_25 = ['E4:BE:ED:A2:2E:7E']
    expected_26 = ['00:1A:3F:86:EC:0A']
    expected_99 = []
    expected_1 = ['58:10:8C:26:DC:30', '58:10:8C:46:8D:67', '58:10:8C:B0:E9:8E', '78:44:76:8F:BB:07',
                  '78:44:76:90:65:0F', '78:44:76:90:C1:27', 'C4:6E:1F:AC:76:27', 'C8:3A:35:7C:FE:30',
                  'E4:BE:ED:1B:64:1B', 'EC:08:6B:88:74:F3']

    self.assertEqual(get_mac_list(show_pon_mac, '25'), expected_25)
    self.assertEqual(get_mac_list(show_pon_mac, '26'), expected_26)
    self.assertEqual(get_mac_list(show_pon_mac, '99'), expected_99)
    self.assertEqual(get_mac_list(show_pon_mac, '1'), expected_1)


if __name__ == '__main__':
  main()
