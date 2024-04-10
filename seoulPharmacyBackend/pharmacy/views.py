from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Pharmacy
from .serializers import PharmacySerializer


@api_view(['GET'])
def PharmacyList(request):
    queryset = Pharmacy.objects.all()
    serializer = PharmacySerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def pharmacyDetails(request, id):
    pharmacy = Pharmacy.objects.get(id=id)
    serializer = PharmacySerializer(pharmacy)
    return Response(serializer.data)

# Create your views here.
