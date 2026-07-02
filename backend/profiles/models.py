"""
User Profile models.

Extends the built-in Django User model with additional profile information
including bio, avatar, location, and social links.
"""
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile linked one-to-one with Django's auth User.

    Stores additional metadata such as biography, avatar image,
    location, website URL, and timestamps for auditing.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        default='',
        help_text='A short biography (max 500 characters).',
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text='Profile picture. Recommended size: 256x256px.',
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='City or region.',
    )
    website = models.URLField(
        max_length=200,
        blank=True,
        default='',
        help_text='Personal or professional website.',
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='Used for age verification; not displayed publicly.',
    )
    is_public = models.BooleanField(
        default=True,
        help_text='Whether this profile is visible to other users.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def display_name(self):
        """Return the user's full name or fall back to username."""
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created,
    or save the existing profile when the User is updated.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
