from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

class UserMatchedArticlePagination(PageNumberPagination):

    page_size = 10
    max_page_size = 100
    page_size_query_param = None

    def get_page_number(self, request, paginator):
        return request.data.get("page", 1)

    def get_paginated_response(self, data):
        return Response({
            "status": "success",
            "count": self.page.paginator.count,
            "data": data
        })
