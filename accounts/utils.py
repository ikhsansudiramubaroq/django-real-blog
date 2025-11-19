
# FUNGSI CEK AUTHOR ATAU USER BIASA
def is_author (user):
    return user.is_authenticated and user.role == 'author'

def is_reader (user):
    return user.is_authenticated and user.role == 'user'
# END CEK ROLE