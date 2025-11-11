from django.contrib import admin

# Register your models here.
from .models import NewsLetter,Contact

admin.site.register(NewsLetter)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')