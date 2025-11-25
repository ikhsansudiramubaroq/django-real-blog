def get_redirect_by_role(user):
    if user.role == 'author':
        return 'author:author_index'
    return 'blog:blog_index'