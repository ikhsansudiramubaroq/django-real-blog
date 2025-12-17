"""
blog/views.py - Views untuk Blog App
Views hanya bertanggung jawab untuk request/response handling.
Business logic ada di blog/services.py
"""
from django.shortcuts import render
from . import services
from .forms import CommentsForm
from .models import Comment


def index(request):
    """Halaman home blog, tampilkan 6 post terbaru."""
    context = {
        'title': 'Pastel - Blog',
        'get_post': services.get_published_posts(limit=6),
    }
    return render(request, 'blog/index.html', context)


def blog_view(request):
    """Halaman semua blog dengan pagination."""
    page_number = request.GET.get('page')
    context = {
        'title': 'Pastel - Blog',
        'get_post': services.get_paginated_posts(page_number),
    }
    return render(request, 'blog/blog.html', context)


def detail_post(request, slug_post):
    """Detail post dengan related posts dan komentar."""
    # Get post detail
    post = services.get_post_detail(slug_post)
    
    # Increment views
    services.increment_post_views(post)
    
    # Get related posts and comments
    related_posts = services.get_related_posts(post)
    comments = services.get_post_comments(post)
    
    # Handle comment form
    if request.method == 'POST':
        form = CommentsForm(request.POST or None)
        if form.is_valid():
            comment_content = request.POST.get('comments')
            reply_id = request.POST.get('reply_slug')
            comments_reply = None

            if reply_id:
                comments_reply = Comment.objects.filter(id=reply_id).first()

            Comment.objects.create(
                post=post,
                user=request.user,
                comments=comment_content,
                reply=comments_reply
            )
            form = CommentsForm()
    else:
        form = CommentsForm()

    # Get author slug if available
    slug_author = None
    if hasattr(post.user, 'author_profile'):
        slug_author = post.user.author_profile.slug_author

    context = {
        'title': post.title_post,
        'detail_post': post,
        'tags': post.tags.all(),
        'related_post': related_posts,
        'form': form,
        'comments': comments,
        'slug_author': slug_author,
    }
    return render(request, 'blog/detail.html', context)


def category_view(request, slug_cat):
    """Halaman category dengan posts dan sidebar data."""
    current_category = services.get_category_detail(slug_cat)
    page_number = request.GET.get('page')
    
    context = {
        'title': f"Category-{current_category.title_cat}",
        'posts': services.get_posts_by_category(current_category, page_number),
        'popular_post_category': services.get_popular_posts_by_category(current_category),
        'popular_tag': services.get_popular_tags_by_category(current_category),
        'current_category': current_category,
        'category': services.get_all_categories()
    }
    return render(request, 'blog/category.html', context)


def tag_view(request, slug):
    """Halaman tag dengan posts dan sidebar data."""
    get_tag = services.get_tag_detail(slug)
    page_number = request.GET.get('page')
    
    context = {
        'title': f"Tag - {slug}",
        'get_tag': get_tag,
        'all_tag': services.get_all_tags(),
        'popular_post_tag': services.get_popular_posts_by_tag(get_tag),
        'posts': services.get_posts_by_tag(get_tag, page_number)
    }
    return render(request, 'blog/tag.html', context)