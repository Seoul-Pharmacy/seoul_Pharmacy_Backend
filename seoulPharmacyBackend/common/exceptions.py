from rest_framework import status
from rest_framework.exceptions import APIException


class PharmacyNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '해당하는 약국이 없습니다.'


class ApiKeyForbidden(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'API 인증키가 유효하지 않습니다.'


class ApiInternalServerError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'API 서버 오류입니다.'


class ApiNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'API 요청에 대한 결과가 없습니다.'


class ApiBadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'API 서버가 요청을 이해할 수 없습니다.'
