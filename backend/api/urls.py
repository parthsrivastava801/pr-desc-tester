from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, NotificationViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'categories', CategoryViewSet)

v1_router = DefaultRouter()
v1_router.register(r'alerts', AlertViewSet, basename='alert')

v2_router = DefaultRouter()
v2_router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('v1/', include(v1_router.urls)),
    path('v2/', include(v2_router.urls)),
]
