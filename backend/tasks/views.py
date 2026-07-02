"""Views for the tasks API."""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tag, Task
from .serializers import TagSerializer, TaskSerializer, TaskListSerializer


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
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title', 'priority', 'due_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return Task.objects.select_related('owner').prefetch_related('tags').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Return all tasks that are past their due date."""
        from django.utils import timezone
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
        ).exclude(status=Task.Status.DONE)
        serializer = TaskListSerializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Return only the current user's tasks."""
        my = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(my)
        if page is not None:
            serializer = TaskListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TaskListSerializer(my, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """CRUD viewset for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name']
    ordering = ['name']
