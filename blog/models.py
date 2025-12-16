from django.db import models

# import slugify
from django.utils.text import slugify
# import setting->auth
from django.conf import settings
# import taggit
from taggit.managers import TaggableManager

# Create your models here.
# model category
class Category(models.Model):
    title_cat = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug_cat = models.SlugField(blank=True, editable=False)
    
    def save(self, *args, **kwargs):
        self.slug_cat = slugify(self.title_cat)
        return super(Category,self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title_cat
    
# class untuk postingan blog
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = TaggableManager()
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='post_likes',
        blank=True
        )
    views = models.IntegerField(default=0)
    weekly_views = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    title_post = models.CharField(max_length=250)
    fill = models.TextField()
    slug_post = models.SlugField(blank=True, unique=True,editable=False)
    images_post = models.ImageField(blank=True,upload_to='post/')
    publish = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    
    def save(self,*args, **kwargs):
        # Logika hanya buat slug jika slug_post BELUM ada
        if not self.slug_post:
            self.slug_post = slugify(self.title_post)
        return super().save(*args,**kwargs) # Gunakan super() yang lebih bersih
    
    def __str__(self):
        return self.title_post

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                            on_delete=models.CASCADE,
                            default=0)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    comments = models.TextField()
    reply = models.ForeignKey('self',related_name='replies',max_length=200,
                            on_delete=models.CASCADE, blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.post.title_post} - {self.comments} - {self.user.nama}"