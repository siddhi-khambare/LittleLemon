
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Booking, Menu


class MenuAPITest(TestCase):
    """Unit tests for Menu API CRUD operations."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin_chef',
            email='chef@littlelemon.com',
            password='AdminPassword123!'
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        self.item1 = Menu.objects.create(
            title="Greek Salad",
            price=12.50,
            inventory=20,
            category=Menu.CATEGORY_STARTERS,
            description="Crispy salad with feta",
            featured=True
        )

        self.item2 = Menu.objects.create(
            title="Bruschetta",
            price=8.99,
            inventory=15,
            category=Menu.CATEGORY_STARTERS,
            description="Grilled sourdough with tomato"
        )

    def test_get_menu_list(self):
        response = self.client.get('/api/menu/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_menu_filter_category(self):
        response = self.client.get('/api/menu/?category=starters')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_post_menu_item_unauthorized(self):
        payload = {
            "title": "Lemon Dessert",
            "price": "6.50",
            "inventory": 30
        }
        response = self.client.post('/api/menu/', payload, format='json')

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )

    def test_post_menu_item_admin(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )

        payload = {
            "title": "Lemon Dessert",
            "price": "6.50",
            "inventory": 30,
            "category": "desserts",
            "description": "Authentic lemon tart"
        }

        response = self.client.post('/api/menu/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.count(), 3)
        self.assertEqual(response.data['title'], "Lemon Dessert")

    def test_get_single_menu_item(self):
        response = self.client.get(f'/api/menu/{self.item1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Greek Salad")

    def test_put_menu_item_admin(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )

        payload = {
            "title": "Greek Salad Supreme",
            "price": "14.00",
            "inventory": 18,
            "category": "starters",
            "description": "Updated greek salad recipe"
        }

        response = self.client.put(
            f'/api/menu/{self.item1.id}/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.title, "Greek Salad Supreme")

    def test_delete_menu_item_admin(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key
        )

        response = self.client.delete(f'/api/menu/{self.item2.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(id=self.item2.id).exists())


class BookingAPITest(TestCase):
    """Unit tests for Booking API CRUD operations."""

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='lemon_customer',
            password='CustomerPass123!',
            email='customer@example.com'
        )

        self.token = Token.objects.create(user=self.user)
        self.future_date = timezone.now() + timedelta(days=2)

        self.booking = Booking.objects.create(
            user=self.user,
            name="Alice Smith",
            no_of_guests=4,
            booking_date=self.future_date
        )

    def test_guest_can_create_booking(self):
        payload = {
            "name": "Bob Vance",
            "no_of_guests": 2,
            "booking_date": (
                timezone.now() + timedelta(days=3)
            ).isoformat()
        }

        response = self.client.post(
            '/api/booking/', payload, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)

    def test_authenticated_booking_attaches_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        payload = {
            "name": "lemon_customer",
            "no_of_guests": 5,
            "booking_date": (
                timezone.now() + timedelta(days=4)
            ).isoformat()
        }

        response = self.client.post(
            '/api/booking/', payload, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_booking = Booking.objects.get(id=response.data['id'])
        self.assertEqual(new_booking.user, self.user)

    def test_unauthenticated_cannot_list_bookings(self):
        response = self.client.get('/api/booking/')

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )

    def test_authenticated_can_list_bookings(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        response = self.client.get('/api/booking/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_put_booking(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        payload = {
            "name": "Alice Smith Updated",
            "no_of_guests": 6,
            "booking_date": (
                timezone.now() + timedelta(days=5)
            ).isoformat()
        }

        response = self.client.put(
            f'/api/booking/{self.booking.id}/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.no_of_guests, 6)

    def test_delete_booking(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        response = self.client.delete(
            f'/api/booking/{self.booking.id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Booking.objects.filter(id=self.booking.id).exists()
        )


class AuthenticationAPITest(TestCase):
    """Unit tests for registration, token login and logout."""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        payload = {
            "username": "new_guest",
            "email": "new_guest@example.com",
            "password": "SecurePassword999!"
        }

        response = self.client.post(
            '/api/register/', payload, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="new_guest")
        self.assertTrue(user.check_password("SecurePassword999!"))
        self.assertNotEqual(user.password, "SecurePassword999!")

    def test_token_auth_valid_credentials(self):
        User.objects.create_user(
            username="login_test",
            password="MyPassword123"
        )

        payload = {
            "username": "login_test",
            "password": "MyPassword123"
        }

        response = self.client.post(
            '/api/api-token-auth/', payload, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_token_auth_invalid_credentials(self):
        User.objects.create_user(
            username="login_test2",
            password="MyPassword123"
        )

        payload = {
            "username": "login_test2",
            "password": "WrongPassword"
        }

        response = self.client.post(
            '/api/api-token-auth/', payload, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_logout(self):
        user = User.objects.create_user(
            username="logout_user",
            password="Pass123456!"
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + token.key
        )

        response = self.client.post('/api/logout/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=token.key).exists())
