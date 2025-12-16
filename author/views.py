from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
# Import Form dari file forms.py di aplikasi yang sama
from .forms import PostForm
from blog.forms import CommentsForm
# import fungsi pada models
from django.db.models import Count, F, Q
# import models
from .models import AuthorProfile
from blog.models import Post, Comment
# import json
import json
# Import fungsi-fungsi dari utils
from .utils.services import get_author_stats, get_total_views,get_author_comments_count, get_published_posts, get_draft_posts, get_author_comments,get_recent_comment, get_view_author_data, update_user_profile, update_profile_picture, is_author

# DRF
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Import serializers
from . import serializers

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api_view(request):
    # Your dashboard logic using services
    stats = get_author_stats(request.user)

    data = {
        'stats': stats,
        'comment_count': get_author_comments_count(request.user),
        'recent_comment': get_recent_comment(request.user),
        'total_views': get_total_views(request.user)
    }

    # For now, return the raw data since the serializer expects instances, not raw data
    return Response(data)

# API endpoint for creating posts
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post_api(request):
    serializer = serializers.PostCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        post = serializer.save()
        return Response({
            'success': True,
            'message': 'Post created successfully',
            'post_id': post.id
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# index author (dashboard)
# FUNGSI CEK AUTHOR
@login_required  # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index')  # Memastikan user adalah Author, jika gagal redirect ke home
def author_index(request):
    user = request.user  # Ambil user yang sedang login
    stats = get_author_stats(user)  # Panggil fungsi untuk mendapatkan statistik dari utils
    comment_count = get_author_comments_count(user)  # Panggil fungsi untuk mendapatkan jumlah komentar dari utils
    recent_comment = get_recent_comment(user)  # Panggil fungsi untuk mendapatkan jumlah komentar dari utils
    total_views = get_total_views(user)
    context = {
        'title' : 'Dashboard Author',
        'stats': stats,  # Tambahkan statistik ke konteks
        'comment_count': comment_count,  # Tambahkan jumlah komentar ke konteks
        'recent_comment': recent_comment,  # Tambahkan jumlah komentar ke konteks
        'total_views' : total_views,
    }
    return render(request, 'author/dashboard_author.html', context)  # Render template dengan konteks


@login_required  # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index')  # Memastikan user adalah Author, jika gagal redirect ke home
def post(request):
    get_post = get_published_posts(request.user)  # Panggil fungsi dari utils untuk mendapatkan post published
    context = {  # Buat konteks untuk template
        'title': 'Daftar Postingan',  # Tambahkan judul ke konteks
        'get_post': get_post,  # Tambahkan post ke konteks
    }
    return render(request, 'author/post.html', context)  # Render template dengan konteks


@login_required  # Memastikan user sudah login
@user_passes_test(is_author, login_url='blog:blog_index')  # Memastikan user adalah Author, jika gagal redirect ke home
def draft_post(request):
    get_draft_post = get_draft_posts(request.user)  # Panggil fungsi dari utils untuk mendapatkan draft post
    context = {  # Buat konteks untuk template
        'title': 'Draft Post',  # Tambahkan judul ke konteks
        'get_draft_post': get_draft_post  # Tambahkan draft post ke konteks
    }
    return render(request, 'author/draft_post.html', context)  # Render template dengan konteks


# === FUNGSI CREATE POST ===
@login_required
@user_passes_test(is_author, login_url='blog:blog_index')  # Lindungi View: Hanya Author yang boleh akses
def create_post(request):
    if request.method == 'POST':  # Cek jika metode request adalah POST
        # Instansiasi form dengan data POST dan request.FILES (penting untuk ImageField)
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user  # Set user yang sedang login sebagai pemilik post
            new_post.save()
            form.save_m2m()  # Simpan hubungan many-to-many dari form
            return redirect('author:list_post')  # Redirect ke halaman list_post
    else:
        form = PostForm()
    context = {
        'title': 'Buat Postingan Baru',
        'form': form
    }
    return render(request, 'author/create_post.html', context)  # Render template dengan konteks


# === FUNGSI EDIT POST ===
@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def edit_post(request, slug_post):
    get_post = Post.objects.get(slug_post = slug_post)
    if request.method == 'POST':  # Cek jika metode request adalah POST
        form = PostForm(request.POST, request.FILES, instance=get_post)  # Buat instance PostForm dengan data POST dan file
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user  # Set user yang sedang login sebagai pemilik post
            new_post.save()
            form.save_m2m()
            return redirect('author:list_post')  # Redirect ke halaman index author
    else:
        form = PostForm(instance=get_post)  # Buat instance PostForm berisi instance 'get_post'
    context = {
        'title': 'Edit Post',  # Tambahkan judul ke konteks
        'form': form  # Tambahkan form ke konteks
    }
    return render(request, 'author/create_post.html', context)  # Render template dengan konteks

# detail view post
@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def detail_post(request, slug_post):
    # Ambil satu post berdasarkan slug dengan relasi category, user, dan tags
    detail_post = get_object_or_404(
        Post.objects.select_related('category', 'user')
        .prefetch_related('tags', 'user__author_profile'),slug_post=slug_post
    )

    # Akses hanya untuk pemilik post
    if request.user != detail_post.user:
        return redirect('author:list_post')

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

    return render (request, 'author/detail_view_post.html', context)


# Profile setting view
@login_required
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
@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
@require_POST
def profile_update(request):
    try:
        # Parse incoming JSON data
        data = json.loads(request.body)  # Ambil data JSON dari body request
        result = update_user_profile(request, data)
        return JsonResponse(result)  # Kembalikan hasil dalam bentuk JSON
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})  # Kembalikan error jika terjadi exception


# API endpoint to update profile picture
@login_required
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
@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def comment_author(request):
    get_comment = get_author_comments(request.user)  # Panggil fungsi dari utils untuk mendapatkan komentar author
    context = {  # Buat konteks untuk template
        'title': 'Daftar Postingan',  # Tambahkan judul ke konteks
        'get_comment': get_comment,  # Tambahkan komentar ke konteks
    }
    return render(request, 'author/author_comment.html', context)  # Render template dengan konteks

@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def delete_comment (request):
    comment_id = request.POST.get("comment_id")
    get_comment = get_object_or_404(Comment, id=comment_id)

    # Cek apakah penghapus adalah author post pemilik comment
    if get_comment.post.user != request.user:
        return HttpResponseForbidden("Kamu tidak punya akses untuk hapus komentar ini!")
    get_comment.delete()
    return redirect("author:author_comment")

# END DASHBOARD AUTHOR



# FRONT END HALAMAN AUTHOR

def view_author(request, slug_author):
    # Ambil data author dari service
    author_data = get_view_author_data(request, slug_author)  # Panggil fungsi dari utils untuk mendapatkan data author
    # Set konteks dengan data dari service
    context = {  # Buat konteks untuk template
        'title': 'View Author',  # Tambahkan judul ke konteks
        'detail_author': author_data['detail_author'],  # Tambahkan detail author ke konteks
        'posts': author_data['posts'],  # Tambahkan post ke konteks
        'serialize_post': author_data['serialize_post'],  # Tambahkan post ke konteks
        'get_category': author_data['get_category'],  # Tambahkan kategori ke konteks
        'get_tag': author_data['get_tag'],  # Tambahkan tag ke konteks
        'comment': author_data['comment'],  # Tambahkan komentar terbaru ke konteks
        'author_id': author_data['user'].id,  # Pass author ID for JavaScript
    }
    return render(request, 'author/author.html', context)  # Render template dengan konteks
