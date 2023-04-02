from django.core.paginator import Paginator

POSTS_ON_PAGE = 10


def paginate(post_list, page_number, posts_on_page=POSTS_ON_PAGE):
    paginator = Paginator(post_list, posts_on_page)
    page_obj = paginator.get_page(page_number)
    return page_obj
