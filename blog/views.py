from django.shortcuts import render,redirect, get_object_or_404
from django.http import Http404
from .models import *
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from taggit.models import Tag

# Create your views here.

# halaman home blog, tampilkan kategori berdasarkan banyaknya blog
def index(request):
    
    # Prefetch tags agar efisien (1 query join)
    get_post = (
        Post.objects.all()
        .select_related('category', 'user') #join kode (efisien)
        .prefetch_related('tags')           #prefetch many to many
        .order_by('-publish')               #urutkan terbaru
    )
    
    # add paginator
    paginate = Paginator(get_post, 4) # Show 6 articles per page
    page_number = request.GET.get('page') # get('page') adalah fungsi dari paginator
    post = paginate.get_page(page_number) # get_page adalah fungsi dari paginator
    
    # Hitung tag populer dengan sekali query
    popular_tags = (
        Tag.objects.annotate(post_count=Count('post'))
        .order_by('-post_count')[:10]  # ambil 10 tag terpopuler
    )
    
    
    # LOGIKA EFISIEN UNTUK MENGAMBIL CATEGORY + COUNT DALAM 1 QUERY
    get_category = Category.objects.annotate(
        # Hitung jumlah postingan yang berelasi. 
        # 'post' adalah related_name default dari ForeignKey Post.category.
        post_count=Count('post', distinct=True) 
        # tampilkan category dengan paling banyak postingan
    ).order_by('-post_count')
    
    # Ambil 3 artikel dengan views terbanyak
    popular_post = (
        Post.objects.select_related('user', 'category')
        .order_by('-views')[:3]
    )
    
    context = {
        'title': 'Pastel - Blog',
        'get_post': post, #post adalah hasil dari paginate
        'popular_tags': popular_tags, #tag yang ditampilkan
        'get_category' : get_category,
        'popular_post': popular_post,
    }
    return render (request, 'blog/index.html', context)

# detail post
def detail_post(request, slug_post):
    # Ambil satu post berdasarkan slug dengan relasi category, user, dan tags
    detail_post = get_object_or_404(
        Post.objects.select_related('category', 'user')
        .prefetch_related('tags'),slug_post=slug_post
    )
    
    # Ambil semua tag yang terkait dengan postingan ini
    tags = detail_post.tags.all()
    
    # Ambil artikel terkait
    related_post = (
        #cari artikel dengan tag sama
        Post.objects.filter(
            Q(tags__in=tags) | Q(category=detail_post.category)  #fallback kalau tag nggak cocok
        )
        .exclude(id=detail_post.id) #jangan tampilkan artikel yang sedang dibuka
        .select_related('category', 'user')
        .prefetch_related('tags')
        .annotate(shared_tags=Count('tags')) #ranking berdasar jumlah tag sama
        .order_by('-shared_tags', '-views')[:3] #urutkan tag terbanyak lalu views terbanyak
    )
    
    # Tambahkan counter views (opsional, efisien di PostgreSQL)
    Post.objects.filter(pk=detail_post.pk).update(views=F('views') + 1)
    
    # tag = Tag.objects.all()
    context = {
        'title' : detail_post.title_post,
        'detail_post' : detail_post,
        'tags' : tags,
        'related_post': related_post
    }
    return render (request, 'blog/detail.html', context)