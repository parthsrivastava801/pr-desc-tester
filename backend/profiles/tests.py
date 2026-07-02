"""
Tests for the User Profile API endpoints.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import UserProfile

User = get_user_model()


class UserProfileModelTest(TestCase):
    """Tests for the UserProfile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )

    def test_profile_created_automatically(self):
        """A profile should be auto-created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_display_name_uses_full_name(self):
        """display_name should return full name when available."""
        self.assertEqual(self.user.profile.display_name, 'Test User')

    def test_display_name_falls_back_to_username(self):
        """display_name should fall back to username when no full name."""
        user = User.objects.create_user(username='noname', password='pass123')
        self.assertEqual(user.profile.display_name, 'noname')

    def test_str_representation(self):
        self.assertEqual(str(self.user.profile), 'Profile of testuser')


class ProfileAPITest(TestCase):
    """Tests for profile API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )

    def test_list_profiles_returns_public_only(self):
        """GET /api/profiles/ should only return public profiles."""
        self.other_user.profile.is_public = False
        self.other_user.profile.save()

        response = self.client.get('/api/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [p['username'] for p in response.data['results']]
        self.assertIn('apiuser', usernames)
        self.assertNotIn('otheruser', usernames)

    def test_search_profiles_by_username(self):
        """GET /api/profiles/?search=api should filter results."""
        response = self.client.get('/api/profiles/', {'search': 'api'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_my_profile_requires_auth(self):
        """GET /api/profiles/me/ should require authentication."""
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_profile_returns_own_profile(self):
        """GET /api/profiles/me/ should return the logged-in user's profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'apiuser')

    def test_update_own_profile(self):
        """PATCH /api/profiles/me/ should update the profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/api/profiles/me/',
            {'bio': 'Hello world', 'location': 'San Francisco'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Hello world')
        self.assertEqual(response.data['location'], 'San Francisco')

    def test_cannot_update_other_users_profile(self):
        """PUT on another user's profile should be denied."""
        self.client.force_authenticate(user=self.user)
        other_profile_id = self.other_user.profile.id
        response = self.client.put(
            f'/api/profiles/{other_profile_id}/',
            {'bio': 'hacked'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
