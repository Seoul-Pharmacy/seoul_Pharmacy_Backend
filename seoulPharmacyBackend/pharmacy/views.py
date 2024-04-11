from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Pharmacy
from .serializers import PharmacySerializer


@api_view(['GET'])
def pharmacy_list(request) -> Response:
    gu = request.GET.get("gu")
    language = request.GET.get("language", default=None)
    day_of_week = request.GET.get("dayOfWeek")
    open_time = request.GET.get("openTime")
    close_time = request.GET.get("closeTime")

    pharmacies = Pharmacy.objects.filter(gu=gu)
    pharmacies = filter_by_language(pharmacies, language)
    pharmacies = filter_by_dayofweek_and_time(pharmacies, day_of_week, open_time, close_time)

    page = request.GET.get("page")
    paginator = Paginator(pharmacies, 10)
    pages = paginator.page(page)

    serializer = PharmacySerializer(pharmacies, many=True)
    return Response(serializer.data)


def filter_by_language(queryset, language) -> QuerySet:
    if language == "en":
        return queryset.filter(speaking_english=True)
    if language == "cn":
        return queryset.filter(speaking_chinese=True)
    if language == "jp":
        return queryset.filter(speaking_japanese=True)
    return queryset


def filter_by_dayofweek_and_time(queryset, day_of_week, open_time, close_time) -> QuerySet:
    if day_of_week == "mon":
        queryset.filter(mon_open_time=open_time, mon_close_time=close_time)
    elif day_of_week == "tue":
        queryset.filter(tue_open_time=open_time, tue_close_time=close_time)
    elif day_of_week == "wed":
        queryset.filter(wed_open_time=open_time, wed_close_time=close_time)
    elif day_of_week == "thu":
        queryset.filter(thu_open_time=open_time, thu_close_time=close_time)
    elif day_of_week == "fri":
        queryset.filter(fri_open_time=open_time, fri_close_time=close_time)
    elif day_of_week == "sat":
        queryset.filter(sat_open_time=open_time, sat_close_time=close_time)
    elif day_of_week == "sun":
        queryset.filter(sun_open_time=open_time, sun_close_time=close_time)
    return queryset


@api_view(['POST'])
def pharmacy_save(request) -> Response:
    serializer = PharmacySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PharmacyDetails(View):
    def get(self, request, id) -> JsonResponse:
        pharmacy = Pharmacy.objects.get(id=id)
        serializer = PharmacySerializer(pharmacy)
        return JsonResponse(serializer.data)

    def post(self, request, id) -> JsonResponse:
        try:
            query = Pharmacy.objects.get(id=id)
        except Pharmacy.DoesNotExist as e:
            return JsonResponse({'error': {
                'code': 404,
                'message': "Pharmacy not found!"
            }}, status=status.HTTP_404_NOT_FOUND)

        pharmacy = PharmacySerializer(query, data=request.data)
        if pharmacy.is_valid():
            pharmacy.save()
            return JsonResponse(pharmacy.data)
        return JsonResponse(pharmacy.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id) -> JsonResponse:
        try:
            query = Pharmacy.objects.get(id=id)
        except Pharmacy.DoesNotExist:
            return JsonResponse({'error': {
                'code': 404,
                'message': "User not found!"
            }}, status=status.HTTP_404_NOT_FOUND)

        query.delete()
        return JsonResponse(status=status.HTTP_204_NO_CONTENT)
