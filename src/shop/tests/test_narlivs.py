import decimal
from unittest import mock
from os.path import join, dirname, abspath
from django.test import TestCase
from ..suppliers import get_supplier_api, narlivs

TESTDATA_DIR = join(dirname(abspath(__file__)), 'data')


class NarlivsTest(TestCase):
    def setUp(self):
        self.report_path = join(TESTDATA_DIR, 'delivery_report.pdf')

    def test_pdf_to_text(self):
        text = narlivs.pdf_to_text(self.report_path)
        self.assertTrue('001337' in text)

    def test_receive_delivery(self):
        api = get_supplier_api('narlivs')
        items = api.parse_delivery_report(self.report_path)
        self.assertEqual(len(items), 32)
        for item in items:
            self.assertEqual(len(item.sku), 9)

    @mock.patch('narlivs.Narlivs.get_product')
    def test_retrieve_product(self, mock_narlivs):
        m = mock_narlivs.return_value = mock.MagicMock()
        m.data = {
            'name': 'GOOD KEBABA',
            'price': decimal.Decimal('13.37'),
            'units': 2
        }
        api = get_supplier_api('narlivs')
        product = api.retrieve_product('1337')
        self.assertEqual(product.name, 'Good Kebaba')
        self.assertEqual(product.price, decimal.Decimal('13.37'))
        self.assertEqual(product.units, 2)

    @mock.patch('narlivs.Narlivs.get_cart')
    def test_order_product(self, mock_get_cart):
        m = mock_get_cart.return_value = mock.MagicMock()
        api = get_supplier_api('narlivs')
        api.order_product('1337', 2)
        m.add_product.assert_has_calls([
            mock.call('1337'),
            mock.call('1337')
        ])
