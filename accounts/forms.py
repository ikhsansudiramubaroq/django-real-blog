from django import forms 

from .models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['nama','email','no_hp','password1','password2']

