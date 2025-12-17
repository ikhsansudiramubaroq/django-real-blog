"""
author/views.py - Template Views untuk Author App
File ini hanya berisi views yang merender template HTML.
Semua API views (DRF) ada di author/api/views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden

# Forms
from .forms import PostForm
from blog.forms import CommentsForm

# Models
from .models import AuthorProfile
from blog.models import Post, Comment

# Services (Business Logic Layer)
from .services.business import (
    is_author,
    get_author_stats,
    get_author_comments_count,
    get_recent_comments,
    get_total_views_stats,
    get_published_posts,
    get_draft_posts,
    get_author_comments,
    get_view_author_page_data,
    increment_post_view,
    get_related_posts
)


# --- TEMPLATE VIEWS (Standard Django) ---

@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def author_index(request):
    """Dashboard utama untuk author."""
    user = request.user
    context = {
        'title': 'Dashboard Author',
        'stats': get_author_stats(user),
        'comment_count': get_author_comments_count(user),
        'recent_comment': get_recent_comments(user),
        'total_views': get_total_views_stats(user),
    }
    return render(request, 'author/dashboard_author.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def post(request):
    """Daftar postingan published milik author."""
    context = {
        'title': 'Daftar Postingan',
        'get_post': get_published_posts(request.user),
    }
    return render(request, 'author/post.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def draft_post(request):
    """Daftar postingan draft milik author."""
    context = {
        'title': 'Draft Post',
        'get_draft_post': get_draft_posts(request.user),
    }
    return render(request, 'author/draft_post.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def create_post(request):
    """Form untuk membuat postingan baru."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            form.save_m2m()
            return redirect('author:list_post')
    else:
        form = PostForm()
    
    context = {
        'title': 'Buat Postingan Baru',
        'form': form
    }
    return render(request, 'author/create_post.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def edit_post(request, slug_post):
    """Form untuk mengedit postingan."""
    get_post = get_object_or_404(Post, slug_post=slug_post)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=get_post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            form.save_m2m()
            return redirect('author:list_post')
    else:
        form = PostForm(instance=get_post)
    
    context = {
        'title': 'Edit Post',
        'form': form
    }
    return render(request, 'author/create_post.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def detail_post(request, slug_post):
    """Detail view untuk postingan dengan komentar."""
    # Fetch Post
    detail_post = get_object_or_404(
        Post.objects.select_related('category', 'user')
        .prefetch_related('tags', 'user__author_profile'),
        slug_post=slug_post
    )

    # Check ownership
    if request.user != detail_post.user:
        return redirect('author:list_post')

    # Increment view
    increment_post_view(detail_post)

    # Related Posts
    related_post = get_related_posts(detail_post)
    
    # Comments
    comment_post = Comment.objects.filter(post=detail_post, reply=None).order_by('-timestamp')

    # Comment Form Handling
    if request.method == 'POST':
        form = CommentsForm(request.POST or None)
        if form.is_valid():
            comment_content = request.POST.get('comments')
            reply_id = request.POST.get('reply_slug')
            comments_reply = None
            if reply_id:
                comments_reply = Comment.objects.filter(id=reply_id).first()

            Comment.objects.create(
                post=detail_post,
                user=request.user,
                comments=comment_content,
                reply=comments_reply
            )
            form = CommentsForm()
    else:
        form = CommentsForm()

    slug_author = None
    if hasattr(detail_post.user, 'author_profile'):
        slug_author = detail_post.user.author_profile.slug_author

    context = {
        'title': detail_post.title_post,
        'detail_post': detail_post,
        'tags': detail_post.tags.all(),
        'related_post': related_post,
        'form': form,
        'comments': comment_post,
        'slug_author': slug_author,
    }

    return render(request, 'author/detail_view_post.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def setting_profile_author(request):
    """Halaman setting profil author."""
    author_profile, created = AuthorProfile.objects.get_or_create(user=request.user)
    context = {
        'title': 'Setting Profile',
        'author_profile': author_profile,
        'user': request.user,
    }
    return render(request, 'author/setting_profile_author.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def comment_author(request):
    """Daftar komentar pada postingan milik author."""
    context = {
        'title': 'Daftar Komentar',
        'get_comment': get_author_comments(request.user),
    }
    return render(request, 'author/author_comment.html', context)


@login_required
@user_passes_test(is_author, login_url='blog:blog_index')
def delete_comment(request):
    """Hapus komentar dari postingan author."""
    comment_id = request.POST.get("comment_id")
    get_comment = get_object_or_404(Comment, id=comment_id)

    if get_comment.post.user != request.user:
        return HttpResponseForbidden("Kamu tidak punya akses untuk hapus komentar ini!")
    
    get_comment.delete()
    return redirect("author:author_comment")


# --- PUBLIC AUTHOR VIEW ---

def view_author(request, slug_author):
    """Halaman profil author yang bisa diakses publik."""
    data = get_view_author_page_data(request, slug_author)
    
    context = {
        'title': 'View Author',
        'detail_author': data['detail_author'],
        'posts': data['posts'],
        'get_category': data['categories'],
        'get_tag': data['tags'],
        'comment': data['comments'],
        'author_id': data['user'].id,
    }
    return render(request, 'author/author.html', context)
