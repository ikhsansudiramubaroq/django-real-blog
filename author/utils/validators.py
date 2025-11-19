# validators.py - Fungsi-fungsi untuk validasi input

import re
from django.core.exceptions import ValidationError


def validate_email_format(email):
    """Validasi format email menggunakan regex"""
    # Pola regex untuk validasi email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Cek apakah email cocok dengan pola
    if not re.match(pattern, email):
        # Jika tidak cocok, raise ValidationError
        raise ValidationError('Format email tidak valid')


def validate_phone_number(phone):
    """Validasi format nomor telepon"""
    # Hapus karakter spesial untuk pemeriksaan dasar
    clean_phone = re.sub(r'[^\d+]', '', phone)
    # Cek apakah hanya berisi angka dan panjang yang wajar
    if len(clean_phone) < 10 or len(clean_phone) > 15:
        # Jika panjang tidak sesuai, raise ValidationError
        raise ValidationError('Nomor telepon harus antara 10-15 digit')


def validate_image_file(image):
    """Validasi apakah file adalah gambar"""
    # Cek apakah file memiliki atribut name
    if hasattr(image, 'name'):
        # Dapatkan ekstensi file
        ext = image.name.split('.')[-1].lower()
        # Daftar ekstensi gambar yang diperbolehkan
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        # Cek apakah ekstensi dalam daftar yang diperbolehkan
        if ext not in allowed_extensions:
            # Jika tidak diperbolehkan, raise ValidationError
            raise ValidationError(f'Format file {ext} tidak didukung. Gunakan JPG, JPEG, PNG, GIF, atau WebP')


def validate_slug_format(slug):
    """Validasi format slug"""
    # Pola regex untuk slug (hanya huruf, angka, tanda hubung, dan underscore)
    pattern = r'^[a-z0-9_-]+$'
    # Cek apakah slug cocok dengan pola
    if not re.match(pattern, slug):
        # Jika tidak cocok, raise ValidationError
        raise ValidationError('Slug hanya boleh berisi huruf kecil, angka, tanda hubung, dan underscore')