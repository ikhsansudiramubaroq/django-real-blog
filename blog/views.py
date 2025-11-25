from django.shortcuts import render,redirect, get_object_or_404
from django.http import Http404
from .models import *
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from taggit.models import Tag
from .forms import CommentsForm

# Create your views here.

# halaman home blog, tampilkan kategori berdasarkan banyaknya blog
def index(request):

    # Prefetch tags agar efisien (1 query join)
    get_post = (
        Post.objects.filter(status='published')
        .select_related('category', 'user') #join kode (efisien)
        .prefetch_related('tags')           #prefetch many to many
        .order_by('-publish')[:6]            #urutkan terbaru
    )

    context = {
        'title': 'Pastel - Blog',
        'get_post': get_post,
    }
    return render (request, 'blog/index.html', context)

# view untuk menampilkan semua blog,semua kategori dan semua tag serta search
# halaman home blog, tampilkan kategori berdasarkan banyaknya blog
def blog_view(request):

    # Prefetch tags agar efisien (1 query join)
    get_post = (
        Post.objects.filter(status='published')
        .select_related('category', 'user') #join kode (efisien)
        .prefetch_related('tags')           #prefetch many to many
        .order_by('-publish')               #urutkan terbaru
    )

    # add paginator
    paginate = Paginator(get_post, 4) # Bagi daftar posts menjadi potongan kecil, masing-masing berisi 4 item.
    page_number = request.GET.get('page') # Coba cek di URL, user lagi di halaman ke berapa? GET bagian dari request, dan get bagian dar GET
    post = paginate.get_page(page_number) # Dari kumpulan semua posts, ambil hanya bagian yang sesuai dengan nomor halaman get_number.

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
    ).order_by('-post_count')[:4]

    # Ambil 3 artikel dengan views terbanyak
    popular_post = (
        Post.objects.filter(status='published')
        .select_related('user', 'category')
        .order_by('-views')[:3]
    )

    context = {
        'title': 'Pastel - Blog',
        'get_post': post, #post adalah hasil dari paginate
        'popular_tags': popular_tags, #tag yang ditampilkan
        'get_category' : get_category,
        'popular_post': popular_post,
    }
    return render (request, 'blog/blog.html', context)

# detail post
def detail_post(request, slug_post):
    # Ambil satu post berdasarkan slug dengan relasi category, user, dan tags
    detail_post = get_object_or_404(
        Post.objects.select_related('category', 'user')
        .prefetch_related('tags', 'user__author_profile'),slug_post=slug_post
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

    # ambil comment sesuai dengan postingan terkait
    comment_post = Comment.objects.filter(post=detail_post, reply=None).order_by('-timestamp')

    # fungsi comment
    if request.method == 'POST':
        form = CommentsForm(request.POST or None)
        if form.is_valid():
            comment = request.POST.get('comments')
            reply = request.POST.get('reply_slug')
            comments_reply = None

            if reply:
                comments_reply = Comment.objects.get(id=reply)

            comment = Comment.objects.create(post=detail_post,user=request.user,
                                            comments=comment,reply=comments_reply)
            form = CommentsForm()
    else:
        form=CommentsForm()

    # Ambil slug_author dari author profile jika ada
    slug_author = None
    if hasattr(detail_post.user, 'author_profile'):
        slug_author = detail_post.user.author_profile.slug_author

    # tag = Tag.objects.all()
    context = {
        'title' : detail_post.title_post,
        'detail_post' : detail_post,
        'tags' : tags,
        'related_post': related_post,
        'form' : form,
        'comments' : comment_post,
        'slug_author': slug_author,
    }
    return render (request, 'blog/detail.html', context)

# halaman untuk category
def category_view(request,slug_cat ):

    # ambil category yang sedang dibuka + jumlah post
    current_category = get_object_or_404 (
        Category.objects.annotate(
            post_count=Count('post', distinct=True)
        ),
        slug_cat=slug_cat
    )

    # ambil semua category untuk looping category
    category = Category.objects.annotate(
        post_count=Count('post', distinct=True)
    ).order_by('-post_count')

    # ambil semua post berdasarkan category ini
    posts = (
        Post.objects.filter(category=current_category, status='published')
        .select_related('category', 'user')
        .prefetch_related('tags')
        .order_by('-publish')
    )

    paginate = Paginator(posts,4)
    get_number = request.GET.get('page')
    get_post_category = paginate.get_page(get_number)

    # Ambil 3 artikel dengan views terbanyak di category ini
    popular_post_category = (
    Post.objects.filter(category=current_category)
    .select_related('user', 'category')
    .order_by('-views')[:3]
    )

    # hitung 10 tag populer di category tersebut
    popular_tag = (
        Tag.objects.filter(post__category=current_category)
        .annotate(total_post=Count('post', distinct=True))
        .order_by('-total_post')[:10]
    )

    context = {
        'title' : f"Category-{current_category.title_cat}",
        'posts' : get_post_category,
        'popular_post_category' : popular_post_category,
        'popular_tag' : popular_tag,
        'current_category' : current_category,
        'category' : category
    }
    return render(request,'blog/category.html', context)

def tag_view(request, slug):
    # all tag
    all_tag = Tag.objects.annotate(post_count=Count('taggit_taggeditem_items')).order_by('-post_count')

    # ambil tag yang sedang dibuka + jumlah post
    get_tag = get_object_or_404 (
        Tag.objects.annotate(
            post_count=Count('taggit_taggeditem_items', distinct=True)
        ),
        slug=slug
    )

    post = (
        Post.objects.filter(tags=get_tag, status='published') #filter sesuai dengan kondisi
        .select_related('category', 'user') #join setiap postingan ke foreignkey
        .prefetch_related('tags') #join query ManyToManyField Tag
        .order_by('-publish')
    )

    paginate = Paginator(post, 4)
    page_number = request.GET.get('page')
    get_post_tag = paginate.get_page(page_number)

    # Ambil 3 postingan dengan views terbanyak di tag ini
    popular_post_tag = (
    Post.objects.filter(tags=get_tag)
    .select_related('user', 'category')
    .order_by('-views')[:3]
    )

    context = {
        'title': f"Tag - {slug}",
        'get_tag': get_tag,
        'all_tag': all_tag,
        'popular_post_tag' : popular_post_tag,
        'posts' : get_post_tag
    }

    return render(request, 'blog/tag.html', context)