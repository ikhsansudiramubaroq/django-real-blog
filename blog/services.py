"""
blog/services.py - Business Logic Layer untuk Blog App
Berisi fungsi-fungsi yang menghandle business logic untuk blog.
Views hanya bertanggung jawab untuk request/response handling.
"""
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Comment, Category
from taggit.models import Tag


def get_published_posts(limit=None, order_by='-publish'):
    """
    Ambil daftar post yang sudah dipublish dengan relasi yang dioptimasi.
    """
    qs = (
        Post.objects.published()
        .select_related('category', 'user')
        .prefetch_related('tags')
        .order_by(order_by)
    )
    if limit:
        return qs[:limit]
    return qs


def get_paginated_posts(page_number, per_page=4):
    """
    Ambil paginated posts untuk halaman blog.
    """
    posts = get_published_posts()
    paginator = Paginator(posts, per_page)
    return paginator.get_page(page_number)


def get_post_detail(slug_post):
    """
    Ambil detail post dengan relasi yang dioptimasi.
    """
    return get_object_or_404(
        Post.objects.select_related('category', 'user')
        .prefetch_related('tags', 'user__author_profile'),
        slug_post=slug_post
    )


def get_related_posts(post, limit=3):
    """
    Cari artikel terkait berdasarkan tags dan category.
    Prioritas: jumlah tag yang sama, lalu views terbanyak.
    """
    tags = post.tags.all()
    return (
        Post.objects.filter(Q(tags__in=tags) | Q(category=post.category))
        .exclude(id=post.id)
        .select_related('category', 'user')
        .prefetch_related('tags')
        .annotate(shared_tags=Count('tags'))
        .order_by('-shared_tags', '-views')[:limit]
    )


def increment_post_views(post):
    """
    Increment view counter tanpa mengubah 'update' timestamp.
    """
    Post.objects.filter(pk=post.pk).update(
        views=F('views') + 1,
        weekly_views=F('weekly_views') + 1
    )


def get_post_comments(post):
    """
    Ambil komentar root (bukan reply) untuk sebuah post.
    """
    return Comment.objects.filter(post=post, reply=None).order_by('-timestamp')


def get_category_detail(slug_cat):
    """
    Ambil category dengan jumlah post.
    """
    return get_object_or_404(
        Category.objects.annotate(post_count=Count('post', distinct=True)),
        slug_cat=slug_cat
    )


def get_all_categories():
    """
    Ambil semua category dengan jumlah post.
    """
    return Category.objects.annotate(
        post_count=Count('post', distinct=True)
    ).order_by('-post_count')


def get_posts_by_category(category, page_number, per_page=4):
    """
    Ambil paginated posts berdasarkan category.
    """
    posts = (
        Post.objects.published()
        .filter(category=category)
        .select_related('category', 'user')
        .prefetch_related('tags')
        .order_by('-publish')
    )
    paginator = Paginator(posts, per_page)
    return paginator.get_page(page_number)


def get_popular_posts_by_category(category, limit=3):
    """
    Ambil postingan populer berdasarkan category.
    """
    return (
        Post.objects.filter(category=category)
        .select_related('user', 'category')
        .order_by('-views')[:limit]
    )


def get_popular_tags_by_category(category, limit=10):
    """
    Ambil tag populer dalam category tertentu.
    """
    return (
        Tag.objects.filter(post__category=category)
        .annotate(total_post=Count('post', distinct=True))
        .order_by('-total_post')[:limit]
    )


def get_tag_detail(slug):
    """
    Ambil tag dengan jumlah post.
    """
    return get_object_or_404(
        Tag.objects.annotate(post_count=Count('taggit_taggeditem_items', distinct=True)),
        slug=slug
    )


def get_all_tags():
    """
    Ambil semua tags dengan jumlah post.
    """
    return Tag.objects.annotate(
        post_count=Count('taggit_taggeditem_items')
    ).order_by('-post_count')


def get_posts_by_tag(tag, page_number, per_page=4):
    """
    Ambil paginated posts berdasarkan tag.
    """
    posts = (
        Post.objects.published()
        .filter(tags=tag)
        .select_related('category', 'user')
        .prefetch_related('tags')
        .order_by('-publish')
    )
    paginator = Paginator(posts, per_page)
    return paginator.get_page(page_number)


def get_popular_posts_by_tag(tag, limit=3):
    """
    Ambil postingan populer berdasarkan tag.
    """
    return (
        Post.objects.filter(tags=tag)
        .select_related('user', 'category')
        .order_by('-views')[:limit]
    )
