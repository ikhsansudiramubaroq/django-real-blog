from django.urls import path
from .views import * #import semua views

app_name = 'author'
urlpatterns = [
    path('', author_index, name='author_index'),
    path('list_post/', post, name='list_post'),
    path('create_post/', create_post, name='create_post')
]
