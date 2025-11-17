from django.urls import path
from .views import * #import semua views

app_name = 'author'
urlpatterns = [
    # dashboard author
    path('', author_index, name='author_index'),
    path('list_post/', post, name='list_post'),
    path('draft_post/', draft_post, name='draft_post'),
    path('create_post/', create_post, name='create_post'),

    # profile setting
    path('setting_profile/', setting_profile_author, name='setting_profile'),
    path('api/profile_update/', profile_update, name='profile_update'),
    path('api/profile_picture_update/', profile_picture_update, name='profile_picture_update'),

    # page view profile author (FE)
    path('author/<slug:slug_author>',view_author, name="view_author"),

]
