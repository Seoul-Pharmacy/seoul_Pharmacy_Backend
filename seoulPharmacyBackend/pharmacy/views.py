from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Pharmacy
from .serializers import PharmacySerializer

@api_view(['GET'])
def pharmacy_list(request) -> Response:


    pharmacies = Pharmacy.objects.filter()

    page = request.GET.get("page")
    paginator = Paginator(pharmacies, 10)
    pages = paginator.page(page)

    serializer = PharmacySerializer(pharmacies, many=True)
    return Response(serializer.data)


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
