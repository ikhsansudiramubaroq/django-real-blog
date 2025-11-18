from django.shortcuts import redirect
from django.urls import reverse

class BlockAuthorOnBlogMiddleware:
    """
    Middleware untuk block author masuk ke halaman blog biasa
    """
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        user = request.user
        
        # Jika user belum login → tidak perlu diblokir
        if not user.is_authenticated:
            return self.get_response(request)
        
        # jika role bukan author → biarkan akses normal
        if hasattr(user, 'role') and user.role != "author":
            return self.get_response(request)
        
        # Jika author, periksa apakah URL yang diakses adalah blog publik
        blog_paths = [
            "/blog/",
        ]

        # Cek apakah request path dimulai dengan salah satu blog paths
        if any(request.path.startswith(path) for path in blog_paths):
            # redirect author ke dashboard
            return redirect(reverse("accounts:author_dashboard"))

        return self.get_response(request)