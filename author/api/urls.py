"""
author/api/urls.py - URL Routes untuk Author API
Berisi semua REST API endpoints termasuk JWT authentication
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    PostViewSet, 
    DashboardViewSet,
    profile_update,
    profile_picture_update,
    create_post_api
)

# Namespace 'author_api' didefinisikan di parent include (author/urls.py)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='api-post')
router.register(r'dashboard', DashboardViewSet, basename='api-dashboard')

urlpatterns = [
    # Router URLs (e.g. /posts/, /dashboard/)
    path('', include(router.urls)),

    # Profile API endpoints
    path('profile/update/', profile_update, name='profile_update'),
    path('profile/picture/', profile_picture_update, name='profile_picture_update'),
    path('post/create/', create_post_api, name='create_post_api'),

    # JWT Authentication Endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
