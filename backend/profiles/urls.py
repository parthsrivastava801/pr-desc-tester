"""URL routing for the profiles API."""
from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.ProfileListView.as_view(), name='profile-list'),
    path('me/', views.MyProfileView.as_view(), name='my-profile'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
]
