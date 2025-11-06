# impor django models
from django.db import models

# import abstractuser,baseusermanager,permissionmixin
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin

# import timezone
from django.utils import timezone

# class UserManager > untuk mengelola user biasa dan superuser
class UserManager(BaseUserManager):
    # fungsi create user untuk user biasa (parameter diambil dari fungsi form user registrasi)
    def create_user(self, nama, email, password):
        # validasi email dan nama di sisi server ketika create_user dijalankan
        if not email:
            raise ValueError("Pengguna harus memiliki email !")
        if not nama:
            raise ValueError("Nama Harus diisi")
        
        # buat instance user berdasarkan class yang menunjuk object UserManager()
        user = self.model(
            email = self.normalize_email(email),
            nama=nama
        )
        
        # ambil password dari parameter password
        user.set_password(password)
        user.save(using=self.db)
        
        return user
    
    def create_superuser(self, nama, email, password):
        # pada superuser lempar parameter dengan urutan yang sama ke create_user dan dikelola sebagai user biasa dulu
        user = self.create_user(nama, email,password)
        
        # Tambahkan hak akses admin
        user.is_admin = True       # Menandakan user adalah admin (custom field)
        user.is_staff = True       # Agar bisa akses Django Admin
        user.is_superuser = True   # Semua hak tanpa batas
        
        # Update perubahan hak akses & simpan ke database karna prosesnya user disimpan sebagai user biasa yang di kelola create_user 
        user.save(using=self._db)
        
        return user

# NOTED:
# Dengan kata lain: Model (AbstractBaseUser/User) menentukan APA isinya, 
# sementara Manager (BaseUserManager) menentukan BAGAIMANA isinya dibuat dan diatur.

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User Biasa'),
        ('author', 'Penulis'),
    )
    
    nama = models.CharField(max_length=100)
    job = models.CharField(max_length=50)
    tempat_lahir = models.CharField(max_length=50)
    tanggal_lahir = models.DateTimeField(blank=True, default=timezone.now)
    email = models.EmailField(unique=True, blank=True)
    no_hp = models.CharField(blank=True, null=True)
    img_user = models.ImageField(upload_to='user/', default='user/profile-default.jpg', blank=True)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # control class user oleh UserManager()
    objects = UserManager()

    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['nama']
    
    # __str__ = tampilan representasi teks dari objek, biar lebih mudah dibaca manusia.
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # Semua user punya permission (disederhanakan)
        return True
    
    def has_module_perms(self, app_label):
        # Semua user bisa akses semua modul (disederhanakan)
        return True
    

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Pastikan satu user hanya bisa follow user lain sekali
        unique_together = ('follower', 'following')