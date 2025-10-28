from django.shortcuts import render,redirect 
from django.contrib.auth import logout as Logout
from .forms import RegisterUserForm
from django.contrib import messages

# Create your views here.
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
            form.save()
            return redirect('accounts:login')
        
    else:
        form = RegisterUserForm()
        
    context = {
        'title' : "Register User",
        'form' : form,
    }
    return render (request, 'registration/register.html',context)

def logout(request):
    Logout(request)
    return redirect('accounts:login')