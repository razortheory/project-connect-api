from collections import OrderedDict

from django.conf import settings

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StaticLightPageNumberPaginator(PageNumberPagination):
    """
    The idea is to get rid of all unnecessary requests like count and make urls predictable,
    so we don't allow custom page size here and removing count from response
    """
    page_size_query_param = None
    page_size = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
        ]))


class SchoolsPaginator(StaticLightPageNumberPaginator):
    page_size = settings.SCHOOLS_LIST_PAGE_SIZE
