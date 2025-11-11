# main/forms.py
from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            'name', 'email', 'subject', 'message',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].widget.attrs.update({
            'class':'form-control',
            'placeholder':'Masukan nama lengkap'
        })
        self.fields['email'].widget.attrs.update({
            'class':'form-control',
            'placeholder':'Masukan email Anda'
        })
        self.fields['subject'].widget.attrs.update({
            'class':'form-control',
            'placeholder':'Masukan subject pesan'
        })
        self.fields['message'].widget.attrs.update({
            'class':'form-control',
            'placeholder':'Masukan pesan lengkap'
        })
