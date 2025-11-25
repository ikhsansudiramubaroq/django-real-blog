from django.shortcuts import render,redirect 
from django.contrib.auth import logout as Logout
from .forms import RegisterUserForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

# IMPORT SERVICES
from .services import session_service as ss , role_service as rs



# Create your views here.

# fungsi custom login view for session
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    extra_context = {'title': 'Pastel Blog - Login'}
    
    # ketika login sukses → kita override method ini
    def form_valid(self, form):
        response = super().form_valid(form)
        # masukkan session expiry dari folder services
        ss.apply_session_policy(self.request, self.request.user)
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

    # user menjadi parameter yang dikirim ke fungsi tersebut.
    return redirect(rs.get_redirect_by_role(user))

@login_required
def logout(request):
    Logout(request)
    return redirect('accounts:login')
