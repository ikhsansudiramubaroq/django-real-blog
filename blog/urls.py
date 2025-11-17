from . import views #import semua views
from django.urls import path

app_name = 'blog'
urlpatterns = [
    path('', views.index, name='blog_index'),
    path('blog/', views.blog_view, name='blog_view'),
    path('detail_post/<slug:slug_post>/',views.detail_post, name='detail_post'),
    path('category/<slug:slug_cat>',views.category_view, name='category_view'),
    path('tag/<slug>',views.tag_view, name='tag_view'),
]
