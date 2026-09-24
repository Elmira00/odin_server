from rest_framework.pagination import PageNumberPagination


class NewsArticleListPagination(PageNumberPagination):
    page_size = 24
    page_query_param = 'page'

    
