from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
# Import Form dari file forms.py di aplikasi yang sama
from .forms import PostForm
from blog.models import Post, Category

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
    get_post = Post.objects.all()
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

