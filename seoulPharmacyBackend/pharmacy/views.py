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
from common.exceptions import PharmacyNotFoundException, Fobbiden
from .holiday_api import is_holiday
from .machine_learning import filter_by_location
from .models import Pharmacy
from .pharmacy_hours_api import update_pharmacy_hours_list
from .pharmacy_languages_api import update_pharmacy_languages_about_all_gu
from .serializers import PharmacySerializer, SimplePharmacySerializer, SimpleNearbyPharmacySerializer

logger = logging.getLogger('django')


# 구, 시간, 외국어로 검색하기
@api_view(['GET'])
def pharmacy_list(request) -> Response:
    now = datetime.now()
    page = request.GET.get("page")
    gu = request.GET.get("gu", default=None)
    speaking_english: bool = bool(request.GET.get("speakingEnglish", default=False))
    speaking_japanese: bool = bool(request.GET.get("speakingJapanese", default=False))
    speaking_chinese: bool = bool(request.GET.get("speakingChinese", default=False))
    enter_time = convertTimeToDbTime(int(request.GET.get("enterTime")))
    exit_time = convertTimeToDbTime(int(request.GET.get("exitTime")))
    year = int(request.GET.get("year", default=now.year))
    month = int(request.GET.get("month", default=now.month))
    day = int(request.GET.get("day", default=now.day))

    logger.info(
        "views.pharmacy_list() : request(page : {0}, gu : {1}, speaking_english : {2}, speaking_japanese : {3}, "
        "speaking_chinese : {4}, enter_time : {5}, exit_time : {6}, date : {7}.{8}.{9})".format(
            page, gu, speaking_english, speaking_japanese, speaking_chinese, enter_time, exit_time, year, month, day))

    pharmacies = Pharmacy.objects.all().order_by('id')
    pharmacies = filter_by_gu(pharmacies, gu)
    pharmacies = filter_by_language(pharmacies, speaking_english, speaking_japanese, speaking_chinese)
    pharmacies = filter_by_date_and_time(pharmacies, year, month, day, enter_time, exit_time)

    if not pharmacies:
        raise PharmacyNotFoundException

    paginator = CustomPageNumberPagination()
    pages = paginator.paginate_queryset(pharmacies, request)
    datas = SimplePharmacySerializer(pages, many=True).data

    return paginator.get_paginated_response(datas)


# int형식의 time을 db타임에 맞춰주기, 100 -> 2500
def convertTimeToDbTime(time: int) -> int:
    if time < 600:
        time += 2400
    return time


# 구에 해당하는 약국만 필터링, None이면 그대로
def filter_by_gu(queryset, gu) -> QuerySet:
    if gu is not None:
        queryset = queryset.filter(gu=gu)
    return queryset


# 언어에 맞는 약국만 필터링, None이면 그대로
def filter_by_language(queryset, speaking_english, speaking_japanese, speaking_chinese) -> QuerySet:
    if speaking_english:
        queryset = queryset.filter(speaking_english=True)
    if speaking_japanese:
        queryset = queryset.filter(speaking_japanese=True)
    if speaking_chinese:
        queryset = queryset.filter(speaking_chinese=True)
    return queryset


# 날자에 해당하는 요일 가져오기
def get_day_of_week(year, month, day) -> str:
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    day_of_week = datetime(year, month, day).weekday()

    return days[day_of_week]


# 날짜를 받아서, 그 날짜 운영시간에 해당하는 약국 필터링(요일, 공휴일)
def filter_by_date_and_time(queryset: QuerySet, year: int, month: int, day: int, enter_time: int, exit_time: int):
    if is_holiday(year, month, day):
        return queryset.filter(holiday_open_time__lte=enter_time, holiday_close_time__gte=exit_time)

    day_of_week = get_day_of_week(year, month, day)
    return filter_by_dayofweek_and_time(queryset, day_of_week, enter_time, exit_time)


# 특정 요일 운영시간에 해당하는 약국만 필터링
def filter_by_dayofweek_and_time(queryset: QuerySet, day_of_week: str, enter_time: int, exit_time: int) -> QuerySet:
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
    speaking_english: bool = bool(request.GET.get("speakingEnglish", default=False))
    speaking_japanese: bool = bool(request.GET.get("speakingJapanese", default=False))
    speaking_chinese: bool = bool(request.GET.get("speakingChinese", default=False))
    latitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    is_open = request.GET.get("isOpen", default=False)

    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    now_time = convertTimeToDbTime(convert_hour_and_minute_to_int(now.hour, now.minute))

    logger.info("views.nearby_pharmacy_list() : request(gu : %s, speaking_english : %s, speaking_japanese : %s,  "
                "speaking_chinese : %s , latitude : %s, longitude : %s, is_open : %s, year-month-day-time : %d-%d-%d-%d" % (
                    gu, speaking_english, speaking_japanese,
                    speaking_chinese, latitude, longitude, is_open, year, month, day, now_time))

    pharmacies = Pharmacy.objects.all()
    pharmacies = filter_by_gu(pharmacies, gu)
    pharmacies = filter_by_language(pharmacies, speaking_english, speaking_japanese, speaking_chinese)

    if is_open:
        pharmacies = filter_by_date_and_time(pharmacies, year, month, day, now_time, now_time)

    if not pharmacies:
        raise PharmacyNotFoundException

    datas = SimpleNearbyPharmacySerializer(pharmacies, many=True).data

    datas = filter_by_location(datas, float(latitude), float(longitude))
    paginator = CustomPageNumberPagination()
    pages = paginator.paginate_queryset(datas, request)

    return paginator.get_paginated_response(pages)


# 시간과 분을 2300등의 형식으로 바꿔주기
def convert_hour_and_minute_to_int(hour, minute):
    return hour * 100 + minute


# 약국 운영시간 저장하기
@api_view(['POST'])
def pharmacies_hours_update(request) -> Response:
    logger.info("views.pharmacies_hours_update()")

    # 권한 확인
    if not request.user.is_superuser:
        raise Fobbiden

    update_pharmacy_hours_list()

    return Response(status=status.HTTP_200_OK)


# 약국 외국어 정보 저장하기
@api_view(['POST'])
def pharmacies_languages_update(request):
    logger.info("views.pharmacies_languages_update()")

    # 권한 확인
    if not request.user.is_superuser:
        raise Fobbiden

    update_pharmacy_languages_about_all_gu()

    return Response(status=status.HTTP_200_OK)


class PharmacyDetails(APIView):

    def get(self, request, id) -> JsonResponse:
        logger.info("views.PharmacyDetails.get()")

        pharmacy = get_object_or_404(Pharmacy, id=id)

        serializer = PharmacySerializer(pharmacy)
        return JsonResponse(serializer.data)

    def put(self, request, id) -> JsonResponse:
        logger.info("views.PharmacyDetails.put()")

        # 권한 확인
        if not request.user.is_superuser:
            raise Fobbiden

        query = get_object_or_404(Pharmacy, id=id)

        pharmacy = PharmacySerializer(query, data=request.data)
        if pharmacy.is_valid():
            pharmacy.save()
            return JsonResponse(pharmacy.data)

        return JsonResponse(pharmacy.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id) -> Response:
        logger.info("views.PharmacyDetails.delete()")

        # 권한 확인
        if not request.user.is_superuser:
            raise Fobbiden

        pharmacy = get_object_or_404(Pharmacy, id=id)

        pharmacy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
