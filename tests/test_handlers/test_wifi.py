from unittest import TestCase

from tasiap.handlers.wifi import get_ssid_from_args, get_wifi_password_from_args


class TestArgsFunctions(TestCase):

  def test_get_ssid_from_args(self):
    args_a = ['1234', 'rede', '<!ISPName', '-', 'Família!>']
    expected_args_a_result = 'ISPName - Família'

    args_b = ['1234', 'rede', '<!**WIFI', 'NOWW!>']
    expected_args_b_result = '**WIFI NOWW'

    args_c = ['1234', 'rede', '<!Maria!>']
    expected_args_c_result = 'Maria'

    args_d = ['1234', 'rede', '<!erro']
    expected_args_d_result = None

    args_e = ['1234', 'rede', '<!double', 'able', 'name', 'done!>', 'senha', '<:12345678:>']
    expected_args_e_result = 'double able name done'

    self.assertEqual(get_ssid_from_args(args_a), expected_args_a_result)
    self.assertEqual(get_ssid_from_args(args_b), expected_args_b_result)
    self.assertEqual(get_ssid_from_args(args_c), expected_args_c_result)
    self.assertEqual(get_ssid_from_args(args_d), expected_args_d_result)
    self.assertEqual(get_ssid_from_args(args_e), expected_args_e_result)

  def test_get_wifi_password_from_args(self):
    args_a = ['1234', 'rede', '<!ISPName', '-', 'Família!>']
    expected_args_a_result = None

    args_b = ['1234', 'rede', '<@double', 'able', 'name', 'done@>', 'senha', '<:12345678:>']
    expected_args_b_result = '12345678'

    args_c = ['1234', 'senha', '<:senhacom', 'espaço:>']
    expected_args_c_result = 'senhacom espaço'

    args_d = ['1234', 'senha', '<:senhacom']
    expected_args_d_result = None

    self.assertEqual(get_wifi_password_from_args(args_a), expected_args_a_result)
    self.assertEqual(get_wifi_password_from_args(args_b), expected_args_b_result)
    self.assertEqual(get_wifi_password_from_args(args_c), expected_args_c_result)
    self.assertEqual(get_wifi_password_from_args(args_d), expected_args_d_result)
