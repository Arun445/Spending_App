
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from api import models
User = get_user_model()


def sample_user(email='test@email.com', password='password123'):
    # Create a sample user
    return User.objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        # Test creating a new user with an email successfull
        email = 'johndoe@email.com'
        password = 'password123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test the email for a new user is normalized
        email = 'johndoe@EMAIL.com'

        user = User.objects.create_user(email, '123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Test creating user with no email raises error
        with self.assertRaises(ValueError):
            User.objects.create_user(None, '123')

    def test_create_new_super_user(self):
        # Test creating new super user
        user = User.objects.create_superuser(
            'johndoe@EMAIL.com',
            'password123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_transaction_str(self):
        # Test the transaction string representation
        user = sample_user()
        wallet = models.Wallet.objects.create(
            user=user,
            name='testwallet',
            balance=100,
            currency='EUR'
        )
        transaction = models.Transaction.objects.create(
            user=user,
            flow='expenses',
            wallet=wallet,
            date='2021-09-02T14:07:09',
            category='car',
            note='gas',
            ammount=5,
        )
        self.assertEqual(str(transaction), transaction.category)

    def test_wallet_str(self):
        # Test the wallet string representation
        wallet = models.Wallet.objects.create(
            user=sample_user(),
            name='testwallet',
            balance=100,
            currency='EUR'
        )
        self.assertEqual(str(wallet), wallet.name)

    def test_tag_str(self):
        # Test the ingriedient string representation
        tag = models.Tag.objects.create(name='Card')
        self.assertEqual(str(tag), tag.name)

    @patch('uuid.uuid4')
    def test_transaction_file_name_uuid(self, mock_uuid):
        # Test that image is saved in the correct location
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.transaction_image_file_path(None, 'myimage.jpg')
        exp_path = f'uploads/transaction/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
