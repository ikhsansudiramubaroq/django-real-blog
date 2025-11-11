from django.urls import path
from . import views

app_name = 'contact'
urlpatterns = [
    path('contact/', views.Contact, name='contact'),
    path('subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
