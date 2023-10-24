from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPaginator(PageNumberPagination):
    '''паджинатор для вывода на странице ограниченного числа элементов.'''
    page_size_query_param = 'limit'
    limit = 6
