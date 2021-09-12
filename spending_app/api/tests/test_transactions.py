import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from api.models import Transaction, Wallet, Tag
from api.serializers import TransactionSerializer, TransactionDetailSerializer

TRANSACTION_URL = reverse('api:transaction-list')

User = get_user_model()


def image_upload_url(transaction_id):
    # Return URL for transaction image upload
    return reverse('api:transaction-upload-image', args=[transaction_id])


def transaction_detail_url(transaction_id):
    # Return transaction detail url
    return reverse('api:transaction-detail', args=[transaction_id])


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

        response = self.client.post(TRANSACTION_URL, payload)

        exist = Transaction.objects.filter(
            user=self.user,
            note=payload['note']
        ).exists()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exist)

    def test_create_recipe_with_tags_successful(self):
        # Test creating a recipe with tags
        tag1 = create_sample_tag(self.user, 'testtag')
        tag2 = create_sample_tag(self.user, 'testtag')
        payload = {
            "flow": "expenses",
            "date": "2021-09-02T14:07:09",
            "wallet": self.wallet.id,
            'tags': [tag1.id, tag2.id],
            "category": "food",
            "ammount": 5,
        }

        response = self.client.post(TRANSACTION_URL, payload)
        transaction = Transaction.objects.get(id=response.data['id'])
        tags = transaction.tags.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)

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

    def test_partial_transaction_update_recipe(self):
        # Test updating a transaction with patch
        transaction = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='car',
            ammount=5,
        )
        transaction.tags.add(create_sample_tag(user=self.user, name='testtag'))
        new_tag = create_sample_tag(user=self.user, name='testtag1')

        payload = {'category': 'house', 'tags': new_tag.id}
        url = transaction_detail_url(transaction.id)
        self.client.patch(url, payload)

        transaction.refresh_from_db()
        self.assertEqual(transaction.category, payload['category'])
        tags = transaction.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_transaction_update_recipe(self):
        # Test updating a transaction with put
        transaction = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='car',
            ammount=5,
        )
        transaction.tags.add(create_sample_tag(user=self.user, name='testtag'))

        payload = {'category': 'salary',
                   'flow': 'income',
                   'date': '2021-09-12T14:07:09',
                   'wallet': self.wallet.id,
                   'ammount': 50,
                   }
        url = transaction_detail_url(transaction.id)
        self.client.put(url, payload)
        transaction.refresh_from_db()
        self.assertEqual(transaction.ammount, payload['ammount'])
        self.assertEqual(transaction.flow, payload['flow'])
        tags = transaction.tags.all()

        self.assertEqual(len(tags), 0)

    def test_filter_transactions(self):
        # Test returning transactions with filtered notes,categorys or tags
        transaction1 = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='food',
            ammount=40,
        )
        transaction2 = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            note='testnote1',
            category='car',
            ammount=50,
        )

        transaction1.tags.add(create_sample_tag(
            user=self.user, name='testtag'))
        transaction2.tags.add(create_sample_tag(
            user=self.user, name='testtag1'))

        response1 = self.client.get(TRANSACTION_URL, {'keyword': '1'})
        # Test filter by tags
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), 1)

        response2 = self.client.get(TRANSACTION_URL, {'keyword': 'foo'})
        # Test filter by category
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data), 1)
        self.assertEqual(response2.data[0]['category'], transaction1.category)

        response3 = self.client.get(TRANSACTION_URL, {'keyword': 'testnote'})
        # Test filter by notes
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response3.data), 1)
        self.assertEqual(response3.data[0]['note'], transaction2.note)

    def test_filter_transactions_invalid(self):
        # Test returning recipes with specific tags
        transaction1 = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='food',
            ammount=40,
        )
        transaction2 = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=self.wallet,
            category='car',
            ammount=50,
        )

        transaction1.tags.add(create_sample_tag(
            user=self.user, name='testtag'))
        transaction2.tags.add(create_sample_tag(
            user=self.user, name='testtag1'))

        response = self.client.get(TRANSACTION_URL, {'keyword': '123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        # test setup with an auth user, wallet and a transaction
        self.client = APIClient()
        self.user = User.objects.create_user(
            'testmail@email.com', 'password123')
        self.client.force_authenticate(self.user)
        wallet = self.wallet = Wallet.objects.create(
            user=self.user, name='testwallet', currency='EUR', balance=100)
        self.transaction = Transaction.objects.create(
            user=self.user,
            flow='expenses',
            date='2021-09-02T14:07:09',
            wallet=wallet,
            category='car',
            ammount=5,
        )

    def tearDown(self):
        self.transaction.image.delete()

    def test_upload_image_to_transaction_successful(self):
        # Test uploading an image to transaction successfuly
        url = image_upload_url(self.transaction.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            response = self.client.post(
                url, {'image': ntf}, format='multipart')
        self.transaction.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.transaction.image.path))

    def test_upload_image_bad_request(self):
        # Test upload an invalid image
        url = image_upload_url(self.transaction.id)
        response = self.client.post(
            url, {'image': 'notimage'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
