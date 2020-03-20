from unittest import TestCase, main

from authorize_onu import format_onu_type


class TestStringFunctions(TestCase):

  def test_format_onu_type(self):

    onu_type_a = 'AN5506-01-A1'
    onu_type_b = 'AN5506-04-F1'
    onu_type_c = 'HG260'

    self.assertEqual(format_onu_type(onu_type_a), '5506-01-a1')
    self.assertEqual(format_onu_type(onu_type_b), '5506-04-f1')
    self.assertEqual(format_onu_type(onu_type_c), 'hg260')


if __name__ == '__main__':
  main()