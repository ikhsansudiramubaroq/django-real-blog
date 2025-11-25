from django.utils.text import slugify
# serializers.py - Fungsi-fungsi untuk mengubah data ke format yang bisa dikirim ke template atau API

def serialize_post(post):
    """Konversi objek post ke format dictionary untuk dikirim ke template"""
    # Ambil tags terlebih dahulu
    post_tags = [tag.name for tag in post.tags.all()]

    # Konversi objek post ke format dictionary
    return {
        'id': post.id,  # ID post
        'title_post': post.title_post,  # Judul post
        'fill': post.fill,  # Isi konten post
        'images_post': {
            'url': post.images_post.url if post.images_post else None  # Objek dengan property URL
        },
        'category': post.category.title_cat if post.category else None,  # Nama kategori jika ada
        'tags': post_tags,  # Daftar nama tag
        'tags_count': len(post_tags),  # Jumlah tag untuk template
        'status': post.status,  # Status post (draft/published)
        'views': post.views,  # Jumlah tampilan
        'publish': post.publish,  # Tanggal publikasi
        'update': post.update,  # Tanggal update
        'slug_post': post.slug_post,  # Slug post
        'user': {  # Informasi user pembuat post
            'id': post.user.id,
            'nama': post.user.nama,
            'img_user': {
                'url': post.user.img_user.url if post.user.img_user else None
            },
        } if post.user else None,
    }


def serialize_comment(comment):
    """Konversi objek comment ke format dictionary untuk dikirim ke template"""
    # Konversi objek comment ke format dictionary
    return {
        'id': comment.id,  # ID komentar
        'comments': comment.comments,  # Isi komentar
        'user': {
            'id': comment.user.id,
            'nama': comment.user.nama,
            'img_user': {
                'url': comment.user.img_user.url if hasattr(comment.user, 'img_user') and comment.user.img_user else None
            },
        } if comment.user else None,
        'timestamp': comment.timestamp,  # Waktu komentar dibuat
        'post': {  # Informasi post terkait
            'id': comment.post.id,
            'title_post': comment.post.title_post,
            'slug_post': comment.post.slug_post,
        } if comment.post else None,
    }


def serialize_author_profile(author_profile):
    """Konversi objek author_profile ke format dictionary untuk dikirim ke template"""
    # Konversi objek author profile ke format dictionary
    return {
        'id': author_profile.id,  # ID profile
        'bio': author_profile.bio,  # Bio author
        'social_media': author_profile.social_media,  # Info media sosial
        'slug_author': author_profile.slug_author,  # Slug author
        'user': {  # Informasi user terkait
            'id': author_profile.user.id,
            'nama': author_profile.user.nama,
            'email': author_profile.user.email,
            'img_user': {
                'url': author_profile.user.img_user.url if author_profile.user.img_user else None
            },
        } if author_profile.user else None,
    }