from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Transaction, Wallet, Tag
from api.serializers import TransactionSerializer, TransactionDetailSerializer

TRANSACTION_URL = reverse('api:transaction-list')

User = get_user_model()


def transaction_detail_url(recipe_id):
    # Return transaction detail url
    return reverse('api:transaction-detail', args=[recipe_id])


def create_sample_tag(user, name):
    # Creates and returns a sample tag
    return Tag.objects.create(user=user, name=name)


class PublicTransactionsApiTests(TestCase):
    # Test the publicly available Transaction API

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Test that logi is required for retrieving transactions
        response = self.client.get(TRANSACTION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTransactionsApiTests(TestCase):
    # Test the authorized user tags API

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@email.com', password='password123')
        self.wallet = Wallet.objects.create(
            user=self.user, name='testwallet', currency='EUR', balance=100)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_transactions(self):
        # Test retrieving transactions
        Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-10-02T14:07:09',
            wallet=self.wallet,
            category='car',
            note='gas',
            ammount=5,
        )
        Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='car',
            note='gas',
            ammount=5,
        )

        response = self.client.get(TRANSACTION_URL)

        transactions = Transaction.objects.all().order_by('-date')
        serializer = TransactionSerializer(transactions, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_view_transaction_details(self):
        # Test to view transaction details
        transaction = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='car',
            ammount=5,
        )
        transaction.tags.add(create_sample_tag(self.user, 'baigna'))
        url = transaction_detail_url(transaction.id)
        response = self.client.get(url)
        serializer = TransactionDetailSerializer(transaction, many=False)
        self.assertEqual(response.data, serializer.data)

    def test_transactions_limited_to_user(self):
        # Test that transactions are only for the authenticated user
        user2 = User.objects.create_user(
            email='test2@email.com', password='password123')
        Transaction.objects.create(
            user=user2,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='car',
            note='gas',
            ammount=5,
        )
        transaction = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='food',
            note='salad',
            ammount=5,
        )
        response = self.client.get(TRANSACTION_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['category'], transaction.category)

    def test_create_transaction_successful(self):
        # Test create transaction successful
        payload = {
            "flow": "expenses",
            "date": "2021-09-02T14:07:09",
            "wallet": self.wallet.id,
            "category": "food",
            "note": "salad",
            "ammount": 5,
        }

        self.client.post(TRANSACTION_URL, payload)

        exist = Transaction.objects.filter(
            user=self.user,
            note=payload['note']
        ).exists()
        self.assertTrue(exist)

    def test_create_transaction_invalid(self):
        # Creating a new tag with invalid payload
        payload = {
            'flow': 'expenses',
            'date': '2021-09-02T14:07:09',
            'wallet': self.wallet.id,
            'category': '',
            'note': 'salad',
            'ammount': 5,
        }
        response = self.client.post(TRANSACTION_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
