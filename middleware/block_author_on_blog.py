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
        
        # Cek role = author
        if getattr(user, "role", "") == "author":

            # Path root "/" atau mulai dengan "/blog/"
            if request.path == "/" or request.path.startswith("/blog/"):
                return redirect(reverse("author:author_index"))
        
        return self.get_response(request)