import logging
from datetime import datetime

from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from common.custom_paginations import CustomPageNumberPagination
from common.exceptions import PharmacyNotFoundException
from .models import Pharmacy
from .pharmacy_hours_api import post_pharmacy_hours_list
from .serializers import PharmacySerializer, SimplePharmacySerializer

logger = logging.getLogger('django')


# 구, 시간, 외국어로 검색하기
@api_view(['GET'])
def pharmacy_list(request) -> Response:
    page = request.GET.get("page")
    gu = request.GET.get("gu", default=None)
    language = request.GET.get("language", default=None)
    enter_time = request.GET.get("enterTime")
    exit_time = request.GET.get("exitTime")
    year = int(request.GET.get("year"))
    month = int(request.GET.get("month"))
    day = int(request.GET.get("day"))

    day_of_week = get_day_of_week(year, month, day)

    logger.info(
        "pharmacy list request's page : {0}, gu : {1}, language : {2}, open_time : {3}, close_time : {4}, day_of_week : {5}".format(
            page, gu, language, enter_time, exit_time, day_of_week))

    pharmacies = Pharmacy.objects.all().order_by('id')
    pharmacies = filter_by_gu(pharmacies, gu)
    pharmacies = filter_by_language(pharmacies, language)
    pharmacies = filter_by_dayofweek_and_time(pharmacies, day_of_week, enter_time, exit_time)

    if not pharmacies:
        raise PharmacyNotFoundException

    paginator = CustomPageNumberPagination()
    pages = paginator.paginate_queryset(pharmacies, request)
    datas = SimplePharmacySerializer(pages, many=True).data

    return paginator.get_paginated_response(datas)


# 구에 해당하는 약국만 필터링, None이면 그대로
def filter_by_gu(queryset, gu) -> QuerySet:
    if gu is not None:
        return queryset.filter(gu=gu)
    return queryset


# 언어에 맞는 약국만 필터링, None이면 그대로
def filter_by_language(queryset, language) -> QuerySet:
    if language == "en":
        return queryset.filter(speaking_english=True)
    if language == "cn":
        return queryset.filter(speaking_chinese=True)
    if language == "jp":
        return queryset.filter(speaking_japanese=True)
    return queryset


# 날자에 해당하는 요일 가져오기
def get_day_of_week(year, month, day) -> str:
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    day_of_week = datetime(year, month, day).weekday()

    return days[day_of_week]


# 특정 요일 운영시간에 해당하는 약국만 필터링
def filter_by_dayofweek_and_time(queryset, day_of_week, enter_time, exit_time) -> QuerySet:
    if day_of_week == "mon":
        return queryset.filter(mon_open_time__lte=enter_time, mon_close_time__gte=exit_time)
    elif day_of_week == "tue":
        return queryset.filter(tue_open_time__lte=enter_time, tue_close_time__gte=exit_time)
    elif day_of_week == "wed":
        return queryset.filter(wed_open_time__lte=enter_time, wed_close_time__gte=exit_time)
    elif day_of_week == "thu":
        return queryset.filter(thu_open_time__lte=enter_time, thu_close_time__gte=exit_time)
    elif day_of_week == "fri":
        return queryset.filter(fri_open_time__lte=enter_time, fri_close_time__gte=exit_time)
    elif day_of_week == "sat":
        return queryset.filter(sat_open_time__lte=enter_time, sat_close_time__gte=exit_time)
    elif day_of_week == "sun":
        return queryset.filter(sun_open_time__lte=enter_time, sun_close_time__gte=exit_time)
    return queryset


# # 현재 영업중인지 정보 추가하기
# def addOpenField(datas) -> list:
#     for data in datas:
#         data['open'] = True


# 근처 약국 찾기
@api_view(['GET'])
def nearby_pharmacy_list(request):
    gu = request.GET.get("gu")
    language = request.GET.get("language", default=None)
    latitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    now = datetime.now()
    now_time = now.time()
    day_of_week = get_day_of_week(now.year, now.month, now.day)

    pharmacies = Pharmacy.objects.filter(gu=gu)
    pharmacies = filter_by_language(pharmacies, language)
    pharmacies = filter_by_dayofweek_and_time(pharmacies, day_of_week, now_time, now_time)
    pharmacies = filter_by_location(pharmacies, latitude, longitude)

    if not pharmacies:
        raise PharmacyNotFoundException

    datas = SimplePharmacySerializer(pharmacies, many=True).data

    return Response(datas, status=status.HTTP_200_OK)


# 현재 위도, 경도를 사용하여 가까운 5개 찾기
def filter_by_location(pharmacies, latitude, longitude):
    return pharmacies


# 약국 저장하기
@api_view(['POST'])
def pharmacies_save(request) -> Response:
    post_pharmacy_hours_list()

    return Response(status=status.HTTP_200_OK)


class PharmacyDetails(APIView):

    def get(self, request, id) -> JsonResponse:
        pharmacy = get_object_or_404(Pharmacy, id=id)

        serializer = PharmacySerializer(pharmacy)
        return JsonResponse(serializer.data)

    def put(self, request, id) -> JsonResponse:
        query = get_object_or_404(Pharmacy, id=id)

        pharmacy = PharmacySerializer(query, data=request.data)
        if pharmacy.is_valid():
            pharmacy.save()
            return JsonResponse(pharmacy.data)

        return JsonResponse(pharmacy.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id) -> Response:
        pharmacy = get_object_or_404(Pharmacy, id=id)

        pharmacy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
