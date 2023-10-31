from rest_framework.pagination import PageNumberPagination

from foodgram.settings import LIMIT


class CustomPageNumberPaginator(PageNumberPagination):
    """Паджинатор для вывода на странице ограниченного числа элементов."""
    page_size_query_param = 'limit'
    limit = LIMIT
