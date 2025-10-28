from . import views #import semua views
from django.urls import path

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='blog_index'),
    path('detail_post/<slug:slug_post>/',views.detail_post, name='detail_post')
]
