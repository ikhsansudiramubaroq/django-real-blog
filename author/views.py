from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
# Import Form dari file forms.py di aplikasi yang sama
from .forms import PostForm
from .models import AuthorProfile
import json
# Import fungsi-fungsi dari utils
from .utils.services import get_author_stats, get_author_comments_count, get_author_posts, get_published_posts, get_draft_posts, get_author_comments, get_view_author_data, update_user_profile, update_profile_picture

# Create your views here.
# Asumsi: Kamu sudah memindahkan atau memastikan fungsi ini ada di sini atau di utility.py
def is_author(user):
    """Memeriksa apakah user adalah Author berdasarkan field 'role'."""
    # Asumsi field role == 'author'
    return user.is_authenticated and user.role == 'author'


# index author (dashboard)
# FUNGSI CEK AUTHOR
@login_required(login_url='accounts:login')  # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index')  # Memastikan user adalah Author, jika gagal redirect ke home
def author_index(request):
    user = request.user  # Ambil user yang sedang login
    posts = get_author_posts(user)  # Panggil fungsi untuk mendapatkan post dari utils (sudah diserialisasi)
    stats = get_author_stats(user)  # Panggil fungsi untuk mendapatkan statistik dari utils
    comment_count = get_author_comments_count(user)  # Panggil fungsi untuk mendapatkan jumlah komentar dari utils
    context = {  # Buat konteks untuk template
        'get_post': posts,  # Tambahkan post ke konteks (dalam format serialized)
        'stats': stats,  # Tambahkan statistik ke konteks
        'comment_count': comment_count  # Tambahkan jumlah komentar ke konteks
    }
    return render(request, 'author/dashboard_author.html', context)  # Render template dengan konteks


@login_required(login_url='accounts:login')  # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index')  # Memastikan user adalah Author, jika gagal redirect ke home
def post(request):
    get_post = get_published_posts(request.user)  # Panggil fungsi dari utils untuk mendapatkan post published
    context = {  # Buat konteks untuk template
        'title': 'Daftar Postingan',  # Tambahkan judul ke konteks
        'get_post': get_post,  # Tambahkan post ke konteks
    }
    return render(request, 'author/post.html', context)  # Render template dengan konteks


def draft_post(request):
    get_draft_post = get_draft_posts(request.user)  # Panggil fungsi dari utils untuk mendapatkan draft post
    context = {  # Buat konteks untuk template
        'title': 'Draft Post',  # Tambahkan judul ke konteks
        'get_draft_post': get_draft_post  # Tambahkan draft post ke konteks
    }
    return render(request, 'author/draft_post.html', context)  # Render template dengan konteks


# === FUNGSI CREATE POST ===
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index')  # Lindungi View: Hanya Author yang boleh akses
def create_post(request):
    # 1. Menangani permintaan POST (saat form disubmit)
    if request.method == 'POST':  # Cek jika metode request adalah POST
        # Instansiasi form dengan data POST dan request.FILES (penting untuk ImageField)
        form = PostForm(request.POST, request.FILES)  # Buat instance PostForm dengan data POST dan file
        if form.is_valid():  # Cek jika form valid
            # a. Simpan data tanpa commit ke database dulu
            # commit=False memungkinkan kita memanipulasi objek sebelum disimpan
            new_post = form.save(commit=False)  # Simpan form tanpa commit ke database
            # b. Hubungkan Postingan ke User yang sedang Login (PENTING!)
            new_post.user = request.user  # Set user yang sedang login sebagai pemilik post
            # c. Simpan objek ke database
            new_post.save()  # Simpan objek post ke database
            # d. Simpan hubungan Many-to-Many (Tags)
            # Ini hanya perlu dipanggil jika commit=False digunakan sebelumnya
            form.save_m2m()  # Simpan hubungan many-to-many dari form
            # Redirect ke dashboard Author setelah sukses
            return redirect('author:author_index')  # Redirect ke halaman index author
    # 2. Menangani permintaan GET (saat halaman dibuka)
    else:  # Jika metode request bukan POST
        # Instansiasi form kosong
        form = PostForm()  # Buat instance PostForm kosong
    context = {  # Buat konteks untuk template
        'title': 'Buat Postingan Baru',  # Tambahkan judul ke konteks
        'form': form  # Tambahkan form ke konteks
    }
    return render(request, 'author/create_post.html', context)  # Render template dengan konteks


# === FUNGSI EDIT POST ===
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index')  # Lindungi View: Hanya Author yang boleh akses
def edit_post(request, pk):
    # post = get_object_or_404(Post, id=pk, user=request.user)
    # 1. Menangani permintaan POST (saat form disubmit)
    if request.method == 'POST':  # Cek jika metode request adalah POST
        # Instansiasi form dengan data POST dan request.FILES (penting untuk ImageField)
        form = PostForm(request.POST, request.FILES)  # Buat instance PostForm dengan data POST dan file
        if form.is_valid():  # Cek jika form valid
            # a. Simpan data tanpa commit ke database dulu
            # commit=False memungkinkan kita memanipulasi objek sebelum disimpan
            new_post = form.save(commit=False)  # Simpan form tanpa commit ke database
            # b. Hubungkan Postingan ke User yang sedang Login (PENTING!)
            new_post.user = request.user  # Set user yang sedang login sebagai pemilik post
            # c. Simpan objek ke database
            new_post.save()  # Simpan objek post ke database
            # d. Simpan hubungan Many-to-Many (Tags)
            # Ini hanya perlu dipanggil jika commit=False digunakan sebelumnya
            form.save_m2m()  # Simpan hubungan many-to-many dari form
            # Redirect ke dashboard Author setelah sukses
            return redirect('author:author_index')  # Redirect ke halaman index author
    # 2. Menangani permintaan GET (saat halaman dibuka)
    else:  # Jika metode request bukan POST
        # Instansiasi form kosong
        form = PostForm()  # Buat instance PostForm kosong
    context = {  # Buat konteks untuk template
        'title': 'Buat Postingan Baru',  # Tambahkan judul ke konteks
        'form': form  # Tambahkan form ke konteks
    }
    return render(request, 'author/create_post.html', context)  # Render template dengan konteks


# Profile setting view
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index')
def setting_profile_author(request):
    # Ensure the author profile exists
    author_profile, created = AuthorProfile.objects.get_or_create(user=request.user)  # Dapatkan atau buat profile author
    context = {  # Buat konteks untuk template
        'title': 'Setting Profile',  # Tambahkan judul ke konteks
        'author_profile': author_profile,  # Tambahkan profile author ke konteks
        'user': request.user,  # Explicitly pass the user object to template
    }
    return render(request, 'author/setting_profile_author.html', context)  # Render template dengan konteks


# API endpoint to update profile information
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index')
@require_POST
def profile_update(request):
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)  # Ambil data JSON dari body request
        # Update user fields using service function
        result = update_user_profile(request, data)  # Panggil fungsi update dari utils
        return JsonResponse(result)  # Kembalikan hasil dalam bentuk JSON
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})  # Kembalikan error jika terjadi exception


# API endpoint to update profile picture
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index')
@require_POST
def profile_picture_update(request):
    try:
        if 'img_user' in request.FILES:  # Cek jika ada file img_user di request.FILES
            image = request.FILES['img_user']  # Ambil file image dari request
            # Update profile picture using service function
            result = update_profile_picture(request, image)  # Panggil fungsi update dari utils
            return JsonResponse(result)  # Kembalikan hasil dalam bentuk JSON
        else:
            return JsonResponse({'success': False, 'error': 'No image provided'})  # Kembalikan error jika tidak ada image
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})  # Kembalikan error jika terjadi exception


# comment author
# Profile setting view
@login_required(login_url='accounts:login')
@user_passes_test(is_author, login_url='blog:blog_index')
def comment_author(request):
    get_comment = get_author_comments(request.user)  # Panggil fungsi dari utils untuk mendapatkan komentar author
    context = {  # Buat konteks untuk template
        'title': 'Daftar Postingan',  # Tambahkan judul ke konteks
        'get_comment': get_comment,  # Tambahkan komentar ke konteks
    }
    return render(request, 'author/author_comment.html', context)  # Render template dengan konteks
# END DASHBOARD AUTHOR


def view_author(request, slug_author):
    # Ambil data author dari service
    author_data = get_view_author_data(request, slug_author)  # Panggil fungsi dari utils untuk mendapatkan data author
    # Set konteks dengan data dari service
    context = {  # Buat konteks untuk template
        'title': 'View Author',  # Tambahkan judul ke konteks
        'detail_author': author_data['detail_author'],  # Tambahkan detail author ke konteks
        'posts': author_data['posts'],  # Tambahkan post ke konteks
        'get_category': author_data['get_category'],  # Tambahkan kategori ke konteks
        'get_tag': author_data['get_tag'],  # Tambahkan tag ke konteks
        'comment': author_data['comments'],  # Tambahkan komentar terbaru ke konteks
        'author_id': author_data['user'].id,  # Pass author ID for JavaScript
    }
    return render(request, 'author/author.html', context)  # Render template dengan konteks
