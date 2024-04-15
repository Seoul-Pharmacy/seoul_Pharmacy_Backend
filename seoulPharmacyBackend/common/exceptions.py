from rest_framework import status
from rest_framework.exceptions import APIException


class PharmacyNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '해당하는 약국이 없습니다.'
