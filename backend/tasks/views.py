"""Views for the tasks API."""

from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer, TaskListSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only task owners can edit; everyone else gets read-only access."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD viewset for tasks.

    - List/retrieve: any authenticated user
    - Create: authenticated users (auto-assigns owner)
    - Update/delete: task owner only
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Task.objects.select_related('owner').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
