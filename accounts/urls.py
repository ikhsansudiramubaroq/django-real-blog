from django.urls import path
from . import views #import semua views

from django.contrib.auth.views import (
    PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,
    PasswordResetCompleteView,PasswordChangeView,PasswordChangeDoneView, LogoutView
)

app_name = 'accounts'
urlpatterns = [
    # path('accounts/update_profiles', views.update_profiles, name='update_profiles'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register_user, name='register'),
    # URL perantara yang dipanggil setelah login berhasil
    path('redirect-role/', views.redirect_by_role, name='redirect_by_role'),
    path('author/dashboard/', views.author_dashboard, name='author_dashboard'),
    # path('password_reset/', PasswordResetView.as_view(template_name= "registration/password_reset_form.html"),
    # name='password_reset'),
    # path('password_reset/done/', PasswordResetDoneView.as_view(template_name= "registration/password_reset_done.html"),
    # name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name= "registration/password_reset_confirm.html"),
    # name='password_reset_confirm'),
    # path('reset/done/', PasswordResetCompleteView.as_view(template_name= "registration/password_reset_complete.html"),
    # name='password_reset_confirm'),
    # path('password_change/', PasswordChangeView.as_view(template_name= "registration/password_change_form.html"),
    # name='password_change'),
    # path('password_change/done', PasswordChangeDoneView.as_view(template_name= "registration/password_change_done.html"),
    # name='password_change_done'),
]
