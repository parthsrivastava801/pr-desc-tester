from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Notification
from .tasks import send_email_digest
from django.test import override_settings

class NotificationModelTest(TestCase):
    def test_create_notification(self):
        notification = Notification.objects.create(title="Test", message="Test Message")
        self.assertEqual(notification.title, "Test")
        self.assertEqual(notification.read, False)

class NotificationAPITest(APITestCase):
    def test_v2_notifications(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_v1_alerts_deprecated(self):
        url = reverse('alert-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

class EmailDigestTaskTest(TestCase):
    @override_settings(NOTIFICATIONS_DIGEST_ENABLED=False)
    def test_digest_disabled(self):
        result = send_email_digest()
        self.assertEqual(result, "Email digest is disabled via feature flag.")

    @override_settings(NOTIFICATIONS_DIGEST_ENABLED=True)
    def test_digest_enabled_no_unread(self):
        result = send_email_digest()
        self.assertEqual(result, "No unread notifications to digest.")

    @override_settings(NOTIFICATIONS_DIGEST_ENABLED=True)
    def test_digest_enabled_with_unread(self):
        Notification.objects.create(title="A", message="B")
        result = send_email_digest()
        self.assertEqual(result, "Sent digest for 1 unread notifications.")
