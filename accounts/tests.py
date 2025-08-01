from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass1234'
        )

    def test_dashboard_access_requires_login(self):
        """Should redirect to login if unauthenticated user accesses dashboard."""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_login_logout(self):
        """Test successful login and logout flow."""
        login = self.client.login(username='testuser', password='pass1234')
        self.assertTrue(login)

        dashboard_response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)

        self.client.logout()
        post_logout_response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(post_logout_response.status_code, 302)

    def test_signup(self):
        """Test user sign-up creates a new account successfully."""
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_edit_profile(self):
        """Test updating user profile works as expected."""
        self.client.login(username='testuser', password='pass1234')
        response = self.client.post(reverse('accounts:update_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_change_password_email_flow(self):
        """Test that password reset email view renders successfully."""
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': self.user.email
        })
        self.assertEqual(response.status_code, 302)  # Django redirects on success
