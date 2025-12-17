"""
author/api/views.py - API Views untuk Author App
Semua API views (DRF) terpusat di sini untuk pemisahan yang jelas dari template views.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from blog.models import Post
from author.models import AuthorProfile
from author.services.business import (
    is_author, 
    get_author_stats, 
    get_author_comments_count, 
    get_recent_comments, 
    get_total_views_stats,
    update_user_profile_data,
    update_profile_picture_file
)
from .serializers import (
    PostSerializer, 
    PostWriteSerializer, 
    GlobalDashboardSerializer,
    CommentSerializer
)


# --- PERMISSIONS ---

class IsAuthorPermission(permissions.BasePermission):
    """
    Custom permission to only allow authors to access.
    """
    def has_permission(self, request, view):
        return is_author(request.user)

    def has_object_permission(self, request, view, obj):
        # Only allow author to edit their own posts
        return getattr(obj, 'user', None) == request.user


# --- VIEWSETS ---

class PostViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing posts.
    Automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorPermission]
    lookup_field = 'slug_post'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-update')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostWriteSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DashboardViewSet(viewsets.ViewSet):
    """
    A ViewSet for Dashboard data.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorPermission]

    def list(self, request):
        stats = get_author_stats(request.user)
        comment_count = get_author_comments_count(request.user)
        recent_comments = get_recent_comments(request.user)
        total_views = get_total_views_stats(request.user)

        serializer = GlobalDashboardSerializer({
            'stats': stats,
            'comment_count': comment_count,
            'recent_comments': recent_comments,
            'total_views': total_views
        })
        return Response(serializer.data)


# --- FUNCTION-BASED API VIEWS ---
# Dipindahkan dari author/views.py untuk pemisahan yang bersih

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def profile_update(request):
    """
    API endpoint to update profile information.
    Menggunakan data dari request.data (DRF) untuk update profil user.
    """
    try:
        result = update_user_profile_data(request.user, request.data)
        return Response(result)
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def profile_picture_update(request):
    """
    API endpoint to update profile picture.
    """
    try:
        if 'img_user' in request.FILES:
            result = update_profile_picture_file(request.user, request.FILES['img_user'])
            return Response(result)
        return Response(
            {'success': False, 'error': 'No image provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_post_api(request):
    """
    API Endpoint for creating a post.
    """
    serializer = PostWriteSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        post = serializer.save()
        return Response({
            'success': True,
            'message': 'Post created successfully',
            'post_id': post.id
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
