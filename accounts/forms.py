from django.contrib.auth.forms import UserCreationForm

from .models import User

class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        
        fields = ['nama', 'email', 'no_hp', 'password1', 'password2']