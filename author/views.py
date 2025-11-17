from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
# Import Form dari file forms.py di aplikasi yang sama
from .forms import PostForm
from blog.models import Post, Category, Comment
from django.core.paginator import Paginator
from .models import AuthorProfile
from django.db.models import Count, F, Q
from taggit.models import Tag

# Create your views here.
# Asumsi: Kamu sudah memindahkan atau memastikan fungsi ini ada di sini atau di utility.py
def is_author(user):
    """Memeriksa apakah user adalah Author berdasarkan field 'role'."""
    # Asumsi field role == 'author'
    return user.is_authenticated and user.role == 'author'


# index author (dashboard) 
# FUNGSI CEK AUTHOR
@login_required(login_url='accounts:login') # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index') # Memastikan user adalah Author, jika gagal redirect ke home
def author_index (request):
    return render (request, 'author/dashboard_author.html')

@login_required(login_url='accounts:login') # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index') # Memastikan user adalah Author, jika gagal redirect ke home
def post (request):
    get_post = Post.objects.filter(user=request.user)
    context = {
        'title': 'Daftar Postingan',
        'get_post': get_post,
    }
    return render (request, 'author/post.html', context)

# === FUNGSI CREATE POST ===
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index') # Lindungi View: Hanya Author yang boleh akses
def create_post(request):
    
    # 1. Menangani permintaan POST (saat form disubmit)
    if request.method == 'POST':
        # Instansiasi form dengan data POST dan request.FILES (penting untuk ImageField)
        form = PostForm(request.POST, request.FILES) 
        
        if form.is_valid():
            # a. Simpan data tanpa commit ke database dulu
            # commit=False memungkinkan kita memanipulasi objek sebelum disimpan
            new_post = form.save(commit=False)
            
            # b. Hubungkan Postingan ke User yang sedang Login (PENTING!)
            new_post.user = request.user 
            
            # c. Simpan objek ke database
            new_post.save()
            
            # d. Simpan hubungan Many-to-Many (Tags)
            # Ini hanya perlu dipanggil jika commit=False digunakan sebelumnya
            form.save_m2m() 
            
            # Redirect ke dashboard Author setelah sukses
            return redirect('author:author_index') # Ganti jika nama URL kamu berbeda

    # 2. Menangani permintaan GET (saat halaman dibuka)
    else:
        # Instansiasi form kosong
        form = PostForm()

    context = {
        'title': 'Buat Postingan Baru',
        'form': form
    }
    return render(request, 'author/create_post.html', context)

# === FUNGSI EDIT POST ===
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index') # Lindungi View: Hanya Author yang boleh akses
def edit_post(request,pk):
    
    # post = get_object_or_404(Post, id=pk, user=request.user)

    # 1. Menangani permintaan POST (saat form disubmit)
    if request.method == 'POST':
        # Instansiasi form dengan data POST dan request.FILES (penting untuk ImageField)
        form = PostForm(request.POST, request.FILES) 
        
        if form.is_valid():
            # a. Simpan data tanpa commit ke database dulu
            # commit=False memungkinkan kita memanipulasi objek sebelum disimpan
            new_post = form.save(commit=False)
            
            # b. Hubungkan Postingan ke User yang sedang Login (PENTING!)
            new_post.user = request.user 
            
            # c. Simpan objek ke database
            new_post.save()
            
            # d. Simpan hubungan Many-to-Many (Tags)
            # Ini hanya perlu dipanggil jika commit=False digunakan sebelumnya
            form.save_m2m() 
            
            # Redirect ke dashboard Author setelah sukses
            return redirect('author:author_index') # Ganti jika nama URL kamu berbeda

    # 2. Menangani permintaan GET (saat halaman dibuka)
    else:
        # Instansiasi form kosong
        form = PostForm()

    context = {
        'title': 'Buat Postingan Baru',
        'form': form
    }
    return render(request, 'author/create_post.html', context)
# END DASHBOARD AUTHOR



def view_author(request, slug_author):
    detail_author = get_object_or_404(AuthorProfile, slug_author = slug_author)
    user = detail_author.user #ambil user yang terkait dengan author
    post = Post.objects.filter(user=user)
    
    paginate= Paginator(post, 4)
    page_number = request.GET.get('page')
    get_post_author = paginate.get_page(page_number)
    
    # LOGIKA EFISIEN UNTUK MENGAMBIL CATEGORY + COUNT DALAM 1 QUERY + SESUAI AUTHORNYA
    get_category = (
        Category.objects
        .filter(post__user=user)                #hanya kategori dari postingan author
        .annotate(post_count=Count('post'))     #hitung jumlah post dari setiap kategori
        .order_by('-post_count')                #urutkan dari paling banyak
        .distinct()                             #biar ga dobel kalau join
    )
    
    get_tag = (
        Tag.objects
        .filter(post__user=user)
        .annotate(tag_count=Count('post'))
        .order_by('-tag_count')
    )
    
    
    # ambil semua komentar dari postingan milik author ini
    comments = Comment.objects.filter(post__user=user).order_by('-timestamp')[:5]
    
    context ={
        'title' : 'View Author',
        'detail_author' : detail_author,
        'posts' : get_post_author,
        'get_category' : get_category,
        'get_tag' : get_tag,
        'comment' : comments,
    }
    return render (request, 'author/author.html',context)