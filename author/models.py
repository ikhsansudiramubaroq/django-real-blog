from django.db import models
from django.utils.text import slugify
from django.conf import settings
# Create your models here.

class AuthorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author_profile")
    bio = models.TextField(blank=True)
    social_media = models.JSONField(blank=True, null=True)  # contoh: {"instagram": "https://ig.com/...", "twitter": "..."}
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="following_authors", blank=True)
    slug_author = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.user.nama

    def save(self, *args, **kwargs):
        # otomatis buat slug dari nama user kalau belum ada
        if not self.slug_author:
            self.slug_author = slugify(self.user.nama)
        super().save(*args, **kwargs)