from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StaticLightPageNumberPaginator(PageNumberPagination):
    """
    The idea is to get rid of all unnecessary requests like count and make urls predictable,
    so we don't allow custom page size here and removing count from response
    """
    page_size_query_param = None
    page_size = 10000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
        ]))
