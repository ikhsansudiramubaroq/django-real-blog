# business.py - Business Logic Layer untuk Author App
# Favour returning QuerySets/Objects over Dicts to allow flexibility in Views (Template vs API)

from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from blog.models import Post, Category, Comment
from author.models import AuthorProfile
from author.services.validators import validate_email_format, validate_phone_number, validate_image_file

def is_author(user):
    """
    Check if user has 'author' role.
    """
    return user.is_authenticated and getattr(user, 'role', '') == 'author'

def get_author_stats(user):
    """
    Aggregates post statistics for the author.
    Returns a dictionary of counts.
    """
    return Post.objects.filter(user=user).aggregate(
        total_posts=Count('id'),
        total_draft=Count('id', filter=Q(status='draft')),
        total_published=Count('id', filter=Q(status='published')),
    )

def get_published_posts(user):
    """
    Returns QuerySet of published posts for the user.
    Optimized with select_related for common fields.
    """
    return Post.objects.filter(
        user=user, 
        status='published'
    ).select_related('category', 'user').prefetch_related('tags').order_by('-publish')

def get_draft_posts(user):
    """
    Returns QuerySet of draft posts for the user.
    """
    return Post.objects.filter(
        user=user, 
        status='draft'
    ).select_related('category', 'user').order_by('-update')

def get_author_comments_count(user):
    """
    Returns count of comments on author's posts from the last 7 days.
    """
    one_week_ago = timezone.now() - timedelta(days=7)
    return Comment.objects.filter(
        post__user=user,
        timestamp__gte=one_week_ago
    ).count()

def get_author_comments(user):
    """
    Returns QuerySet of all comments on author's posts.
    """
    return Comment.objects.filter(
        post__user=user
    ).select_related('user', 'post').order_by('-timestamp')

def get_recent_comments(user, limit=5):
    """
    Returns QuerySet of recent comments (last 7 days).
    """
    one_week_ago = timezone.now() - timedelta(days=7)
    return Comment.objects.filter(
        post__user=user,
        timestamp__gte=one_week_ago
    ).select_related('user', 'post').order_by('-timestamp')[:limit]

def refresh_weekly_views(user):
    """
    Resets weekly_views for proper aggregation.
    Command / Side-effect function.
    Ideally run via Cron/Celery, but called here for simplicity in this architecture.
    """
    one_week_ago = timezone.now() - timedelta(days=7)
    # Reset old weekly stats
    Post.objects.filter(
        user=user,
        update__lt=one_week_ago
    ).update(weekly_views=0)

def get_total_views_stats(user):
    """
    Returns dictionary with 'total' and 'week' view counts.
    """
    # Ensure stats are fresh (optional: could be moved to specific trigger)
    refresh_weekly_views(user)
    
    one_week_ago = timezone.now() - timedelta(days=7)
    
    total = Post.objects.filter(user=user).aggregate(sum=Sum('views'))['sum'] or 0
    weekly = Post.objects.filter(
        user=user, 
        update__gte=one_week_ago
    ).aggregate(sum=Sum('weekly_views'))['sum'] or 0
    
    return {'total': total, 'week': weekly}

def get_view_author_page_data(request, slug_author, page_number=1):
    """
    Complex orchestrator for the public Author Page.
    Returns a dictionary of Objects (not dicts) for the View to render.
    """
    # 1. Get Author Profile
    author_profile = get_object_or_404(AuthorProfile, slug_author=slug_author)
    user = author_profile.user
    
    # 2. Get Posts
    posts_qs = Post.objects.filter(user=user, status='published')\
        .select_related('category', 'user')\
        .prefetch_related('tags')\
        .order_by('-publish')
        
    paginator = Paginator(posts_qs, 4)
    page_obj = paginator.get_page(page_number)
    
    # 3. Get Aggregated Category Data
    categories = Category.objects.filter(post__user=user, post__status='published')\
        .annotate(post_count=Count('post'))\
        .order_by('-post_count').distinct()

    # 4. Get Tag Data
    # Note: Tag lookup via reverse relation can be tricky with Taggit, 
    # but strictly following user's original logic pattern:
    tags = Post.tags.most_common() # Global most common, or we filter?
    # Better re-implementation of user's original query:
    from taggit.models import Tag
    tags = Tag.objects.filter(post__user=user, post__status='published')\
        .annotate(tag_count=Count('post'))\
        .order_by('-tag_count')

    # 5. Recent Comments
    comments = Comment.objects.filter(post__user=user)\
        .select_related('post', 'user')\
        .order_by('-timestamp')[:5]

    return {
        'detail_author': author_profile,
        'user': user,
        'posts': page_obj,         # Page object of Post Instances
        'categories': categories,  # QuerySet of Category Instances
        'tags': tags,              # QuerySet of Tag Instances
        'comments': comments,      # QuerySet of Comment Instances
    }

def update_user_profile_data(user, data):
    """
    Updates user profile from data dict.
    """
    email = data.get('email', user.email)
    validate_email_format(email)
    
    phone = data.get('no_hp', user.no_hp)
    validate_phone_number(phone)
    
    user.nama = data.get('nama', user.nama)
    user.email = email
    user.job = data.get('job', user.job)
    user.tempat_lahir = data.get('tempat_lahir', user.tempat_lahir)
    user.tanggal_lahir = data.get('tanggal_lahir', user.tanggal_lahir)
    user.no_hp = phone
    user.save()
    
    # Update AuthorProfile
    author_profile, _ = AuthorProfile.objects.get_or_create(user=user)
    author_profile.bio = data.get('bio', author_profile.bio)
    
    social_media = data.get('social_media', {})
    if social_media:
        current_social = author_profile.social_media or {}
        # Merge updates
        if 'instagram' in social_media:
            current_social['instagram'] = social_media['instagram']
        if 'linkedin' in social_media:
            current_social['linkedin'] = social_media['linkedin']
        author_profile.social_media = current_social
        
    author_profile.save()
    return {'success': True}

def update_profile_picture_file(user, image_file):
    """
    Updates profile picture.
    """
    validate_image_file(image_file)
    user.img_user = image_file
    user.save()
    return {
        'success': True,
        'image_url': user.img_user.url
    }

def get_related_posts(post):
    """
    Finds related posts based on tags and category.
    """
    return Post.objects.filter(
        Q(tags__in=post.tags.all()) | Q(category=post.category)
    ).exclude(id=post.id)\
    .select_related('category', 'user')\
    .prefetch_related('tags')\
    .annotate(shared_tags=Count('tags'))\
    .order_by('-shared_tags', '-views')[:3]

def increment_post_view(post):
    """
    Increments the view counter for a post atomically.
    """
    Post.objects.filter(pk=post.pk).update(views=F('views') + 1)