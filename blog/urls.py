from . import views #import semua views
from django.urls import path

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='blog_index'),
]
