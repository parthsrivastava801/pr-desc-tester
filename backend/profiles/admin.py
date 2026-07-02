"""Admin registration for UserProfile."""
from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin view for managing user profiles."""

    list_display = ['user', 'display_name', 'location', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio', 'location']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
