from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Pharmacy
from .serializers import PharmacySerializer


@api_view(['GET'])
def pharmacyList(request) -> Response:
    pharmacies = Pharmacy.objects.all()
    serializer = PharmacySerializer(pharmacies, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def pharmacySave(request) -> Response:
    serializer = PharmacySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def pharmacyDetails(request, id) -> Response:
    if request.method == 'GET':
        pharmacy = Pharmacy.objects.get(id=id)
        serializer = PharmacySerializer(pharmacy)
        return Response(serializer.data)

    if request.method == 'PUT':
        try:
            query = Pharmacy.objects.get(id=id)
        except Pharmacy.DoesNotExist as e:
            return Response({'error': {
                'code': 404,
                'message': "Pharmacy not found!"
            }}, status=status.HTTP_404_NOT_FOUND)

        pharmacy = PharmacySerializer(query, data=request.data)
        if pharmacy.is_valid():
            pharmacy.save()
            return Response(pharmacy.data)
        return Response(pharmacy.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            query = Pharmacy.objects.get(id=id)
        except Pharmacy.DoesNotExist:
            return Response({'error': {
                'code': 404,
                'message': "User not found!"
            }}, status=status.HTTP_404_NOT_FOUND)

        query.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

