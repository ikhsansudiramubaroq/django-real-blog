def apply_session_policy(request, user):
    # Jika role-nya "author" → session habis saat browser ditutup
    if user.role == 'author':
        request.session.set_expiry(0)
    # User biasa → session panjang (2 minggu)
    else:
        request.session.set_expiry(1209600)