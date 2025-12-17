from django.db.models import Count
from taggit.models import Tag
from .models import Post, Category

def sidebar_data(request):
    """
    Context processor untuk menyediakan data global seperti
    sidebar (Tag Populer, Kategori, Artikel Populer) ke semua template.
    """
    
    # 1. Tag Populer (Top 10)
    popular_tags_global = (
        Tag.objects.annotate(post_count=Count('post'))
        .order_by('-post_count')[:10]
    )

    # 2. Kategori dengan Post Count (Top 5/All)
    categories_global = (
        Category.objects.annotate(
            post_count=Count('post', distinct=True)
        )
        .order_by('-post_count')[:5] # Ambil 5 terpopuler untuk sidebar
    )

    # 3. Artikel Populer (Top 3 by Views)
    popular_posts_global = Post.objects.popular()[:3]

    return {
        'popular_tags': popular_tags_global,
        'get_category': categories_global,
        'popular_post': popular_posts_global,
    }
