from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Pharmacy
from .serializers import PharmacySerializer


# 구, 시간, 외국어로 검색하기
@api_view(['GET'])
def pharmacy_list(request) -> Response:
    page = request.GET.get("page")
    gu = request.GET.get("gu")
    language = request.GET.get("language", default=None)
    open_time = request.GET.get("openTime")
    close_time = request.GET.get("closeTime")
    year = request.GET.get("year")
    month = request.GET.get("month")
    day = request.GET.get("day")

    day_of_week = get_day_of_week(year, month, day)

    pharmacies = Pharmacy.objects.filter(gu=gu)
    pharmacies = filter_by_language(pharmacies, language)
    pharmacies = filter_by_dayofweek_and_time(pharmacies, day_of_week, open_time, close_time)

    paginator = Paginator(pharmacies, 10)
    pages = paginator.page(page)

    datas = PharmacySerializer(pages, many=True).data

    return Response(datas)


# 언어에 맞는 약국만 필터링
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
def filter_by_dayofweek_and_time(queryset, day_of_week, open_time, close_time) -> QuerySet:
    if day_of_week == "mon":
        return queryset.filter(mon_open_time__lte=open_time, mon_close_time__gte=close_time)
    elif day_of_week == "tue":
        return queryset.filter(tue_open_time__lte=open_time, tue_close_time__gte=close_time)
    elif day_of_week == "wed":
        return queryset.filter(wed_open_time__lte=open_time, wed_close_time__gte=close_time)
    elif day_of_week == "thu":
        return queryset.filter(thu_open_time__lte=open_time, thu_close_time__gte=close_time)
    elif day_of_week == "fri":
        return queryset.filter(fri_open_time__lte=open_time, fri_close_time__gte=close_time)
    elif day_of_week == "sat":
        return queryset.filter(sat_open_time__lte=open_time, sat_close_time__gte=close_time)
    elif day_of_week == "sun":
        return queryset.filter(sun_open_time__lte=open_time, sun_close_timev=close_time)
    return queryset


# 현재 영업중인지 정보 추가하기
def addOpenField(datas) -> list:
    for data in datas:
        data['open'] = True


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
    print(pharmacies)

    pharmacies = filter_by_dayofweek_and_time(pharmacies, day_of_week, now_time, now_time)
    print(pharmacies)

    pharmacies = filter_by_location(pharmacies, latitude, longitude)
    print(pharmacies)

    datas = PharmacySerializer(pharmacies, many=True).data

    return Response(datas)


# 현재 위도, 경도를 사용하여 가까운 5개 찾기
def filter_by_location(pharmacies, latitude, longitude):
    return pharmacies


@api_view(['POST'])
def pharmacy_save(request) -> Response:
    serializer = PharmacySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PharmacyDetails(APIView):
    def get(self, request, id) -> JsonResponse:
        pharmacy = Pharmacy.objects.get(id=id)
        serializer = PharmacySerializer(pharmacy)
        return JsonResponse(serializer.data)

    def put(self, request, id) -> JsonResponse:
        try:
            query = Pharmacy.objects.get(id=id)

            pharmacy = PharmacySerializer(query, data=request.data)
            if pharmacy.is_valid():
                pharmacy.save()
                return JsonResponse(pharmacy.data)
        except Pharmacy.DoesNotExist as e:
            return JsonResponse({'error': {
                'code': 404,
                'message': "Pharmacy not found!"
            }}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(pharmacy.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id) -> Response:
        try:
            query = Pharmacy.objects.get(id=id)
        except Pharmacy.DoesNotExist:
            return Response({'error': {
                'code': 404,
                'message': "User not found!"
            }}, status=status.HTTP_404_NOT_FOUND)

        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
