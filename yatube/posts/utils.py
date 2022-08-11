from django.core.paginator import Paginator

from .constants import limitation


def get_page(posts, request):
    paginator = Paginator(posts, limitation)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
