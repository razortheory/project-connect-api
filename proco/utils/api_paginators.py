from collections import OrderedDict

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.translation import gettext_lazy as _

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StaticLightPaginator(Paginator):
    @property
    def num_pages(self):
        # kind of magic variable. just positive number to skip unnecessary checks like display_page_controls
        #  no real impact to pagination behavior due to custom validate_number & page methods
        return 1

    def validate_number(self, number):
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_('That page number is not an integer'))

        if number < 1:
            raise EmptyPage(_('That page number is less than 1'))
        return number

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        return self._get_page(self.object_list[bottom:top], number, self)


class StaticLightPageNumberPaginator(PageNumberPagination):
    """
    The idea is to get rid of all unnecessary requests like count and make urls predictable,
    so we don't allow custom page size here and removing count from response
    """
    page_size_query_param = None
    page_size = 10
    django_paginator_class = StaticLightPaginator

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('results', data),
        ]))


class SchoolsPaginator(StaticLightPageNumberPaginator):
    def get_page_size(self, request):
        return settings.SCHOOLS_LIST_PAGE_SIZE
