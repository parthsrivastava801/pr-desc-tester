"""
API views for User Profiles.
"""
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    UserProfileListSerializer,
)


class ProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/

    List all public user profiles with lightweight serialization.
    Supports search by username via ``?search=<query>`` query param.
    """

    serializer_class = UserProfileListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = UserProfile.objects.filter(is_public=True).select_related('user')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(user__username__icontains=search)
        return qs


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profiles/<pk>/  — Retrieve a profile (public or own).
    PUT  /api/profiles/<pk>/  — Update own profile.
    PATCH /api/profiles/<pk>/ — Partial update own profile.

    Non-public profiles are only visible to their owner.
    """

    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return UserProfile.objects.filter(
                models.Q(is_public=True) | models.Q(user=user)
            ).select_related('user')
        return UserProfile.objects.filter(is_public=True).select_related('user')

    def perform_update(self, serializer):
        """Only allow users to update their own profile."""
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied(
                'You can only update your own profile.'
            )
        serializer.save()


class MyProfileView(APIView):
    """
    GET   /api/profiles/me/  — Retrieve the authenticated user's profile.
    PATCH /api/profiles/me/  — Update the authenticated user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(
            profile, context={'request': request}
        )
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
