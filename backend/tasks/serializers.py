"""Serializers for the tasks API."""

from rest_framework import serializers
from .models import Tag, Task


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']


class TaskSerializer(serializers.ModelSerializer):
    """Full serializer for Task CRUD operations."""

    owner = serializers.ReadOnlyField(source='owner.username')
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source='tags',
        required=False,
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'tags',
            'tag_ids',
            'is_overdue',
            'owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (fewer fields)."""

    owner = serializers.ReadOnlyField(source='owner.username')
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority',
            'due_date', 'is_overdue', 'owner', 'created_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at']
