from django.shortcuts import render
from .models import *
from django.db.models import Count
from taggit.models import Tag
# Create your views here.

def index(request):
    get_post = Post.objects.all()
    # LOGIKA EFISIEN UNTUK MENGAMBIL CATEGORY + COUNT DALAM 1 QUERY
    get_category = Category.objects.annotate(
        # Hitung jumlah postingan yang berelasi. 
        # 'post' adalah related_name default dari ForeignKey Post.category.
        post_count=Count('post', distinct=True) 
        # tampilkan category dengan paling banyak postingan
    ).order_by('-post_count') 
    context = {
        'title': 'Pastel - Blog',
        'get_post': get_post,
        'get_category' : get_category
    }
    return render (request, 'blog/index.html', context)

def detail_post(request, slug_post):
    # Mengambil satu artikel berdasarkan slug yang diklik user.
    detail_post = Post.objects.get(slug_post=slug_post)
    tag = Tag.objects.all()
    context = {
        'title' : 'Detail Postingan',
        'detail_post' : detail_post,
        'tag' : tag
    }
    return render (request, 'blog/detail.html', context)