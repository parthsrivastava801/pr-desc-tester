"""
Serializers for the User Profile API.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Minimal User representation embedded in profile responses."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Full profile serializer for detail / update views.

    Nests a read-only user summary and exposes a computed
    ``display_name`` field.
    """

    user = UserSummarySerializer(read_only=True)
    display_name = serializers.CharField(source='display_name', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'display_name',
            'bio',
            'avatar',
            'avatar_url',
            'location',
            'website',
            'date_of_birth',
            'is_public',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_avatar_url(self, obj):
        """Return absolute URL for the avatar image, or None."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def validate_bio(self, value):
        """Ensure bio doesn't exceed 500 characters."""
        if len(value) > 500:
            raise serializers.ValidationError(
                'Bio must be 500 characters or fewer.'
            )
        return value


class UserProfileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for profile list endpoints."""

    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.CharField(source='display_name', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'display_name',
            'avatar_url',
            'location',
            'is_public',
        ]

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
