"""Serializers for the tasks API."""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Full serializer for Task CRUD operations."""

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (fewer fields)."""

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'status', 'owner', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']
