# services.py - Fungsi-fungsi business logic untuk app author

from django.core.paginator import Paginator
from django.db.models import Count, Q
from taggit.models import Tag
from blog.models import Post, Category, Comment
from author.models import AuthorProfile
# import sum
from django.db.models import Sum

# import time
from django.utils import timezone
from datetime import timedelta

# Import validator dan serializer
from author.utils.validators import validate_email_format, validate_phone_number, validate_image_file
from author.utils.serializers import serialize_post, serialize_comment, serialize_author_profile


# Create your views here.
def is_author(user):
    """Memeriksa apakah user adalah Author berdasarkan field 'role'."""
    # Asumsi field role == 'author'
    return user.is_authenticated and user.role == 'author'

def get_author_stats(user):
    """Mengambil statistik untuk dashboard author"""
    # Query untuk menghitung total post, draft, dan published
    stats = (
        Post.objects.filter(user=user)
        .aggregate(
            total_posts=Count('id'),  # Hitung total post
            total_draft=Count('id', filter=Q(status='draft')),  # Hitung post draft
            total_published=Count('id', filter=Q(status='published')),  # Hitung post published
        )
    )
    # Kembalikan hasil query statistik
    return stats


def get_published_posts(user):
    """Mengambil post-post yang telah dipublish milik author"""
    # Query untuk mengambil post yang statusnya published milik user
    get_post = Post.objects.filter(user=user, status='published')
    # Kembalikan hasil query post published
    return [serialize_post(post) for post in get_post]  # Kembalikan hasil dalam bentuk serialized


def get_draft_posts(user):
    """Mengambil post-post draft milik author"""
    # Query untuk mengambil post yang statusnya draft milik user
    get_draft_post = Post.objects.filter(user=user, status='draft')
    # Kembalikan hasil query post draft
    return [serialize_post(post) for post in get_draft_post]  # Kembalikan hasil dalam bentuk serialized

def get_author_comments_count(user):
    """Menghitung jumlah komentar untuk semua post milik author"""
    # Hitung jumlah komentar dari post-post milik user
    comment_one_week_ago = timezone.now() - timedelta(days=7)
    
    # __gte adalah Ambil semua Comment yang punya timestamp lebih besar atau sama dengan nilai one_week_ago.
    comment_count = Comment.objects.filter(
        post__user=user,timestamp__gte = comment_one_week_ago).count()
    # Kembalikan hasil hitungan komentar
    return comment_count

def get_author_comments(user):
    """Mengambil komentar-komentar untuk post milik author"""
    # Query untuk mengambil komentar yang terkait dengan post milik user
    get_comment = Comment.objects.filter(post__user=user).order_by('-timestamp')
    # Kembalikan hasil query komentar
    return [serialize_comment(comment) for comment in get_comment]  # Kembalikan hasil dalam bentuk serialized

def get_recent_comment(user):
    """Mengambil komentar-komentar untuk post milik author"""
    # Query untuk mengambil komentar yang terkait dengan post milik user
    # # __gte adalah Ambil semua Comment yang punya timestamp lebih besar atau sama dengan nilai one_week_ago.
    comment_one_week_ago = timezone.now() - timedelta(days=7)
    get_comment = Comment.objects.filter(
        post__user=user,
        timestamp__gte = comment_one_week_ago
        ).order_by('-timestamp')[:5]
    # Kembalikan hasil query komentar
    return [serialize_comment(comment) for comment in get_comment]  # Kembalikan hasil dalam bentuk serialized

def get_total_views(user):
    views_one_week_ago = timezone.now() - timedelta(days=7)
    # 1️⃣ Reset weekly_views untuk post yang sudah lewat seminggu
    Post.objects.filter(
        user=user,
        update__lt=views_one_week_ago
    ).update(weekly_views=0)
    # hitung total views
    total_views = Post.objects.filter(user=user).aggregate(total =Sum('views'))
    # views week
    views_week = Post.objects.filter(
        user = user,
        update__gte = views_one_week_ago
    ).aggregate(weekly = Sum('weekly_views'))

    return {'total':total_views['total'] or 0 ,'week': views_week['weekly'] or 0}

def get_view_author_data(request, slug_author):
    """Mengambil data untuk halaman view author"""
    # Ambil profile author berdasarkan slug
    from django.shortcuts import get_object_or_404
    detail_author = get_object_or_404(AuthorProfile, slug_author=slug_author)  # Ambil author berdasarkan slug
    user = detail_author.user  # Ambil user yang terkait dengan author
    # Query untuk mengambil post milik user dengan tags dan category
    post = Post.objects.filter(user=user).prefetch_related('tags').select_related('category', 'user')

    # Buat objek paginator untuk membagi post
    paginate = Paginator(post, 4)  # Buat paginator dengan 4 post per halaman
    # Ambil nomor halaman dari request GET
    page_number = request.GET.get('page')  # Ambil nomor halaman dari request
    # Dapatkan page post sesuai nomor halaman
    get_post_author = paginate.get_page(page_number)  # Dapatkan page post

    # Query untuk mendapatkan category dan jumlah post dalam 1 query sesuai author
    get_category = (  # Query untuk mengambil kategori
        Category.objects  # Mulai dari model Category
        .filter(post__user=user)  # Hanya kategori dari post author
        .annotate(post_count=Count('post'))  # Hitung jumlah post dari setiap kategori
        .order_by('-post_count')  # Urutkan dari paling banyak
        .distinct()  # Agar tidak dobel saat join
    )

    # Query untuk mendapatkan tag dan jumlah post dalam 1 query sesuai author
    get_tag = (  # Query untuk mengambil tag
        Tag.objects  # Mulai dari model Tag
        .filter(post__user=user)  # Filter tag berdasarkan post user
        .annotate(tag_count=Count('post'))  # Hitung jumlah post untuk setiap tag
        .order_by('-tag_count')  # Urutkan dari paling banyak
    )

    # Ambil 5 komentar terbaru dari post milik author dengan post yang terkait
    comments = Comment.objects.filter(post__user=user).select_related('post', 'user').order_by('-timestamp')[:5]  # Query untuk mengambil komentar

    # Kembalikan semua data dalam bentuk dictionary
    return {
        'detail_author': serialize_author_profile(detail_author),  # Detail author dalam format serialized
        'user': user,  # User yang terkait
        'posts': get_post_author,  # Post yang dipaginate
        'serialize_post': [serialize_post(post) for post in get_post_author],  # Serialize tiap post dari Page object (pagination tetap pada 'posts')
        'get_category': get_category,  # Daftar kategori
        'get_tag': get_tag,  # Daftar tag
        'comment': [serialize_comment(comment) for comment in comments],  # Komentar terbaru dalam format serialized
    }

# fungsi detail post
# def get_detail_post (request, slug_post):
#     pass

def update_user_profile(request, data):
    """Perbarui informasi profile pengguna berdasarkan data JSON"""
    try:
        # Validasi data sebelum update
        email = data.get('email', request.user.email)  # Ambil email dari data
        validate_email_format(email)  # Validasi format email

        phone = data.get('no_hp', request.user.no_hp)  # Ambil no_hp dari data
        validate_phone_number(phone)  # Validasi format nomor telepon

        # Update field-field user
        request.user.nama = data.get('nama', request.user.nama)  # Update nama user
        request.user.email = email  # Update email user setelah validasi
        request.user.job = data.get('job', request.user.job)  # Update pekerjaan user
        request.user.tempat_lahir = data.get('tempat_lahir', request.user.tempat_lahir)  # Update tempat lahir user
        request.user.tanggal_lahir = data.get('tanggal_lahir', request.user.tanggal_lahir)  # Update tanggal lahir user
        request.user.no_hp = phone  # Update nomor HP user setelah validasi

        # Simpan perubahan ke database
        request.user.save()  # Simpan user ke database

        # Update profile author
        author_profile, created = AuthorProfile.objects.get_or_create(user=request.user)  # Dapatkan atau buat profile author
        author_profile.bio = data.get('bio', author_profile.bio)  # Update bio

        # Handle data social media
        social_media = data.get('social_media', {})  # Ambil data social media dari request
        if not author_profile.social_media:  # Jika belum ada social media
            author_profile.social_media = {}  # Buat dictionary kosong

        # Update URL Instagram dan LinkedIn
        if 'instagram' in social_media:  # Jika ada data Instagram
            author_profile.social_media['instagram'] = social_media['instagram']  # Update URL Instagram
        if 'linkedin' in social_media:  # Jika ada data LinkedIn
            author_profile.social_media['linkedin'] = social_media['linkedin']  # Update URL LinkedIn

        # Simpan perubahan ke database
        author_profile.save()  # Simpan author profile ke database

        # Kembalikan hasil sukses
        return {'success': True}
    except Exception as e:
        # Jika ada error, kembalikan error
        return {'success': False, 'error': str(e)}


def update_profile_picture(request, image):
    """Perbarui foto profile pengguna"""
    try:
        # Validasi file gambar
        validate_image_file(image)  # Validasi apakah file adalah gambar

        # Set foto baru ke user
        request.user.img_user = image  # Set image baru ke user
        # Simpan perubahan ke database
        request.user.save()  # Simpan user ke database
        # Kembalikan data sukses dan URL foto baru
        return {
            'success': True,  # Status sukses
            'image_url': request.user.img_user.url  # URL foto baru
        }
    except Exception as e:
        # Jika ada error, kembalikan error
        return {'success': False, 'error': str(e)}