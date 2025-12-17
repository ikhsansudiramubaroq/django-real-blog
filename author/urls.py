"""
author/urls.py - URL Routes untuk Author App
API routes didelegasikan ke author.api.urls
"""
from django.urls import path, include
from .views import (
    author_index, post, draft_post, create_post, edit_post, detail_post, 
    comment_author, delete_comment, setting_profile_author, view_author
)
# Import API views untuk profile update (digunakan oleh template dengan AJAX)
from .api.views import profile_update, profile_picture_update

app_name = 'author'

urlpatterns = [
    # API Routes (Delegated to author.api.urls)
    path('api/', include('author.api.urls')),

    # Profile API endpoints (untuk template AJAX - session auth)
    path('api/profile_update/', profile_update, name='profile_update'),
    path('api/profile_picture_update/', profile_picture_update, name='profile_picture_update'),

    # Template Views (Dashboard Author)
    path('', author_index, name='author_index'),
    path('list_post/', post, name='list_post'),
    path('draft_post/', draft_post, name='draft_post'),
    path('create_post/', create_post, name='create_post'),
    path('edit_post/<slug:slug_post>/', edit_post, name='edit_post'),
    path('detail_post/<slug:slug_post>/', detail_post, name='detail_post'),
    path('comment/', comment_author, name='author_comment'),
    path('delete_comment/', delete_comment, name='delete_comment'),

    # Profile setting
    path('setting_profile/', setting_profile_author, name='setting_profile'),
    
    # Page view profile author (Public)
    path('<slug:slug_author>/', view_author, name="view_author"),
]
