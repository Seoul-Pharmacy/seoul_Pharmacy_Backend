from rest_framework import serializers

from pharmacy.models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'


class SimplePharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id', 'name', 'si', 'gu', 'road_name_address', 'main_number', 'speaking_english', 'speaking_japanese',
                  'speaking_chinese']


class SimpleNearbyPharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id', 'name', 'si', 'gu', 'road_name_address', 'main_number', 'speaking_english', 'speaking_japanese',
                  'speaking_chinese', 'latitude', 'longitude']
