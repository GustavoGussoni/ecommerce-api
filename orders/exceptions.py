from rest_framework import status
from rest_framework.exceptions import APIException ,_get_error_details
from django.utils.translation import gettext_lazy as _


class NoStockError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('This product does not have enough items in stock.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = _get_error_details(detail, code)
