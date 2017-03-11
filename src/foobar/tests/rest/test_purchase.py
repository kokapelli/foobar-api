import uuid
from django.core.urlresolvers import reverse_lazy as reverse
from django.conf import settings
from rest_framework import status
from shop.tests.factories import ProductFactory
from wallet.tests.factories import WalletFactory, WalletTrxFactory
from wallet.enums import TrxStatus
from wallet import api as wallet_api
from foobar.rest.fields import MoneyField
from ..factories import AccountFactory
from .base import AuthenticatedAPITestCase
from moneyed import Money
from foobar.api import purchase, get_purchase
from foobar import enums

def serialize_money(x):
    return MoneyField().to_representation(x)


class TestPurchaseAPI(AuthenticatedAPITestCase):
    
    def setUp(self):
        super().setUp()
        self.force_authenticate()
        
    def test_purchase(self):
        account_obj = AccountFactory.create()
        wallet_obj = WalletFactory.create(owner_id=account_obj.id)
        WalletTrxFactory.create(
            wallet=wallet_obj,
            amount=Money(1000, 'SEK'),
            trx_status=TrxStatus.FINALIZED
        )
        product_obj1 = ProductFactory.create(
            name='Billys Ooriginal',
            price=Money(13, 'SEK')
        )
        product_obj2 = ProductFactory.create(
            name='Kebabrulle',
            price=Money(30, 'SEK')
        )
        url = reverse('api:purchases-list')
        data = {
            'account_id': account_obj.id,
            'products': [
                {'id': product_obj1.id, 'qty': 1},
                {'id': product_obj2.id, 'qty': 3},
            ]
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 103)
        _, balance = wallet_api.get_balance(wallet_obj.owner_id, 'SEK')
        self.assertEqual(balance, Money(897, 'SEK'))

    def test_cash_purchase(self):
        product_obj1 = ProductFactory.create(
            name='Billys Ooriginal',
            price=Money(13, 'SEK')
        )
        product_obj2 = ProductFactory.create(
            name='Kebabrulle',
            price=Money(30, 'SEK')
        )
        url = reverse('api:purchases-list')
        data = {
            'account_id': None,
            'products': [
                {'id': product_obj1.id, 'qty': 1},
                {'id': product_obj2.id, 'qty': 3},
            ]
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 103)
        _, balance = wallet_api.get_balance(settings.FOOBAR_CASH_WALLET, 'SEK')
        self.assertEqual(balance, Money(103, 'SEK'))

    def test_purchase_insufficient_funds(self):
        account_obj = AccountFactory.create()
        product_obj1 = ProductFactory.create(
            price=Money(13, 'SEK')
        )
        product_obj2 = ProductFactory.create(
            price=Money(30, 'SEK')
        )
        url = reverse('api:purchases-list')
        data = {
            'account_id': account_obj.id,
            'products': [
                {'id': product_obj1.id, 'qty': 1},
                {'id': product_obj2.id, 'qty': 3},
            ]
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_purchase_invalid_quantity(self):
        account_obj = AccountFactory.create()
        product_obj1 = ProductFactory.create()
        product_obj2 = ProductFactory.create()
        url = reverse('api:purchases-list')
        data = {
            'account_id': account_obj.id,
            'products': [
                {'id': product_obj1.id, 'qty': -5},
                {'id': product_obj2.id, 'qty': 10},
            ]
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_purchase_invalid_product(self):
        account_obj = AccountFactory.create()
        url = reverse('api:purchases-list')
        data = {
            'account_id': account_obj.id,
            'products': [
                {'id': '6c91014d-f444-4ee7-906e-4e1737f7bc58', 'qty': 1},
            ]
        }
        response = self.api_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_list_purchases(self):
        account_obj = AccountFactory.create()
        wallet_obj = WalletFactory.create(owner_id=account_obj.id)
        WalletTrxFactory.create(
            wallet=wallet_obj,
            amount=Money(1000, 'SEK'),
            trx_status=TrxStatus.FINALIZED
        )
        product_obj1 = ProductFactory.create(
            code='1337733113370',
            name='Billys Original',
            price=Money(13, 'SEK')
        )
        products = [
            (product_obj1.id, 3),
        ]

        
        products2 = [
            (product_obj1.id, 2),
        ]

        purchase(account_obj.id, products)
        purchase(account_obj.id, products2)
        purchase(account_obj.id, products2)

        url = reverse('api:purchases-list')

        #Existing  UUID
        response = self.api_client.get(url, {'account_id': account_obj.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        #None existing account
        response = self.api_client.get(url, {'account_id': uuid.uuid4()})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        #Non correct UUID
        response = self.api_client.get(url, {'account_id': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        
    def test_get_purchase(self):
        account_obj = AccountFactory.create()
        wallet_obj = WalletFactory.create(owner_id=account_obj.id)
        WalletTrxFactory.create(
            wallet=wallet_obj,
            amount=Money(1000, 'SEK'),
            trx_status=TrxStatus.FINALIZED
        )
        product_obj1 = ProductFactory.create(
            code='1337733113370',
            name='Billys Original',
            price=Money(13, 'SEK')
        )
        product_obj2 = ProductFactory.create(
            code='7331733113370',
            name='Kebaba',
            price=Money(30, 'SEK')
        )
        products = [
            (product_obj1.id, 3),
            (product_obj2.id, 1),
        ]

        #Correct UUID
        purchase_obj = purchase(account_obj.id, products)
        url = reverse('api:purchases-detail', kwargs={'pk': purchase_obj.id})
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Incorrect UUID
        url = reverse('api:purchases-detail', kwargs={'pk': uuid.uuid4()})
        response = self.api_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
   
        
    def test_cancel_purchase(self):
        account_obj = AccountFactory.create()
        wallet_obj = WalletFactory.create(owner_id=account_obj.id)
        WalletTrxFactory.create(
            wallet=wallet_obj,
            amount=Money(1000, 'SEK'),
            trx_status=TrxStatus.FINALIZED
        )
        product_obj1 = ProductFactory.create(
            code='1337733113370',
            name='Billys Original',
            price=Money(13, 'SEK')
        )
        
        product_obj2 = ProductFactory.create(
            code='7331733113370',
            name='Kebaba',
            price=Money(30, 'SEK')
        )
        products = [
            (product_obj1.id, 3),
            (product_obj2.id, 1),
        ]

        wallet, balance = wallet_api.get_balance(account_obj.id, 'SEK')
        
        purchase_obj = purchase(account_obj.id, products)
        
        url = reverse('api:purchases-detail', kwargs={'pk': purchase_obj.id})

        #Test to see if purchase has gone throuh
        _, balance = wallet_api.get_balance(account_obj.id, 'SEK')
        self.assertEqual(balance, Money(931, 'SEK'))
        
        response = self.api_client.delete(url, format='json')
        
        #Test to see whether money is returned after deletion
        _, balance = wallet_api.get_balance(account_obj.id, 'SEK')
        self.assertEqual(balance, Money(1000, 'SEK'))

        #Check whether status changes to cnaceled
        purchase_obj, _ = get_purchase(purchase_obj.id)
        self.assertEqual(purchase_obj.status, enums.PurchaseStatus.CANCELED)

        
