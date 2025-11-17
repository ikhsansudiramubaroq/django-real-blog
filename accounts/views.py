from django.shortcuts import render,redirect 
from django.contrib.auth import logout as Logout
from .forms import RegisterUserForm
from django.contrib.auth.decorators import login_required, user_passes_test



# FUNGSI CEK AUTHOR ATAU USER BIASA
def is_author(user):
    """Fungsi untuk memeriksa apakah user adalah Author."""
    return user.is_authenticated and user.role == 'author'

def is_reader(user):
    """Fungsi untuk memeriksa apakah user adalah Pembaca biasa."""
    return user.is_authenticated and user.role == 'user'
# END CEK ROLE

# Create your views here.
# PROFILE USER
@login_required
def index_profile(request):
    context = {
        'title' : 'Halaman Profile User'
    }
    return render(request, 'profile_user.html', context)

# fungsi register user
def register_user(request):
    
    if request.method == 'POST':
        form = RegisterUserForm(request.POST or None)
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # ✅ kalau checkbox author dicentang, set role jadi author
            if form.cleaned_data.get('is_author'):
                user.role = 'author'
            else:
                user.role = 'user'  # default misal user biasa
                
            user.save()
            
            return redirect('accounts:login')
        
    else:
        form = RegisterUserForm()
        
    context = {
        'title' : "Register User",
        'form' : form,
    }
    return render (request, 'registration/register.html',context)
# end register User

# FUNGSI REDIRECT SESUAI ROLE
@login_required # Pastikan hanya user yang sudah login yang bisa mengakses ini
def redirect_by_role(request):
    user = request.user
    
    if is_author(user):
        # Arahkan Author ke dashboard khusus
        return redirect('author:author_index')
    
    # Semua user lain (Pembaca) diarahkan ke halaman utama blog
    return redirect('blog:blog_index')

# FUNGSI CEK AUTHOR
@login_required
@user_passes_test(is_author, login_url='accounts:login') # Jika gagal, arahkan ke /login/
def author_dashboard(request):
    # Logika view Dashboard Author
    context = {
        'title': 'Dashboard Author'
    }
    return render(request, 'author/dashboard_author.html', context)

@login_required
def logout(request):
    Logout(request)
    return redirect('accounts:login')


# FUNGSI BUAT POSTINGAN PINDAHKAN KE APP AUTHOR
# @login_required
# @user_passes_test(is_author, login_url='/login/')
# def author_create_post(request):
#     # Logika view untuk membuat artikel baru
#     # ...
#     context = {}
#     return render(request, 'author/create_post.html', context)