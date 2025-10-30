from django import forms
from blog.models import Post

# form create post
class PostForm(forms.ModelForm):
    # Field 'title_post' akan menjadi fokus utama input
    title_post = forms.CharField(
        label='Judul Postingan',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Judul Blog Anda'})
    )
    
    # Field 'fill' (Isi konten)
    fill = forms.CharField(
        label='Isi Konten',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 15})
    )
    
    # Field 'images_post' (Gambar)
    images_post = forms.ImageField(
        label='Gambar Utama',
        required=False, # Gambar tidak wajib diisi saat edit
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    # Field 'category'
    # Django ModelForm otomatis menggunakan Select Widget untuk ForeignKey
    category = forms.ModelChoiceField(
        label='Kategori',
        queryset=Post.category.field.related_model.objects.all(), # Mengambil semua kategori
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Catatan: TaggableManager (tags) akan otomatis dibuat oleh ModelForm, 
    # tetapi kamu mungkin perlu widget khusus jika ingin input tag yang lebih baik.
    
    class Meta:
        model = Post
        fields = [
            'title_post',
            'fill',
            'images_post',
            'category',
            'tags',
            'status', # Author bisa memilih Draft atau Publish
        ]
        
        # Tambahkan widget kustom untuk status
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            # Jika kamu ingin custom widget untuk tags (misalnya input dengan pemisah koma):
            # 'tags': forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput'}),
        }
        
        # Exclude field yang diisi secara otomatis atau tidak perlu ditampilkan
        # Kita tidak perlu menampilkan 'user', 'views', 'slug_post', 'publish', 'update', 'likes'
        exclude = ('user', 'slug_post', 'views', 'likes')

    # Catatan Tambahan: 
    # Field 'user' akan diisi secara otomatis di views.py saat Author menyimpan form.
    # Field 'slug_post' akan diisi oleh method save() di Model Post kamu.