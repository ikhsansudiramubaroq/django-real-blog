from django import forms 

from .models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterUserForm(UserCreationForm):
    # ✅ Checkbox tambahan untuk author
    is_author = forms.BooleanField(
        required=False,
        label="Daftar sebagai Author"
    )
    
    class Meta:
        model = User
        fields = ['nama','email','no_hp','password1','password2', 'is_author']

