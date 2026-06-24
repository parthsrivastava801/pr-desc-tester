from celery import shared_task
from django.conf import settings
from .models import Notification

@shared_task
def send_email_digest():
    if not getattr(settings, 'NOTIFICATIONS_DIGEST_ENABLED', False):
        return "Email digest is disabled via feature flag."
    
    unread_notifications = Notification.objects.filter(read=False).count()
    if unread_notifications > 0:
        # Placeholder for email sending logic
        return f"Sent digest for {unread_notifications} unread notifications."
    return "No unread notifications to digest."
