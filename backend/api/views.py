from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Task, Category, Notification
from .serializers import TaskSerializer, CategorySerializer, NotificationSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer

class AlertViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(
            {"detail": "This endpoint is deprecated. Please use /api/v2/notifications/"},
            status=status.HTTP_410_GONE
        )
