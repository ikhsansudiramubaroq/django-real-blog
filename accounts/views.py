from django.shortcuts import render,redirect 
from django.contrib.auth import logout as Logout
from .forms import RegisterUserForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test

# IMPORT UTILS
from .utils import is_author,is_reader



# Create your views here.

# fungsi custom login view for session
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    extra_context = {'title': 'Pastel Blog - Login'}
    
    # ketika login sukses → kita override method ini
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        
        # Jika role-nya "author" → session habis saat browser ditutup
        if user.role == "author":
            self.request.session.set_expiry(0)
        else:
            # User biasa → session panjang (2 minggu)
            self.request.session.set_expiry(1209600)
        
        return response

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
