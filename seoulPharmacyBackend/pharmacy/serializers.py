from rest_framework import serializers

from pharmacy.models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res['mon_open_time'] = self.convert_int_to_time(res['mon_open_time'])
        res['tue_open_time'] = self.convert_int_to_time(res['tue_open_time'])
        res['wed_open_time'] = self.convert_int_to_time(res['wed_open_time'])
        res['thu_open_time'] = self.convert_int_to_time(res['thu_open_time'])
        res['fri_open_time'] = self.convert_int_to_time(res['fri_open_time'])
        res['sat_open_time'] = self.convert_int_to_time(res['sat_open_time'])
        res['sun_open_time'] = self.convert_int_to_time(res['sun_open_time'])
        res['holiday_open_time'] = self.convert_int_to_time(res['holiday_open_time'])
        res['mon_close_time'] = self.convert_int_to_time(res['mon_close_time'])
        res['tue_close_time'] = self.convert_int_to_time(res['tue_close_time'])
        res['wed_close_time'] = self.convert_int_to_time(res['wed_close_time'])
        res['thu_close_time'] = self.convert_int_to_time(res['thu_close_time'])
        res['fri_close_time'] = self.convert_int_to_time(res['fri_close_time'])
        res['sat_close_time'] = self.convert_int_to_time(res['sat_close_time'])
        res['sun_close_time'] = self.convert_int_to_time(res['sun_close_time'])
        res['holiday_close_time'] = self.convert_int_to_time(res['holiday_close_time'])

        return res

    def convert_int_to_time(self, data):
        if data is None:
            return

        hour = str(data // 100).zfill(2)
        minute = str(data % 100).zfill(2)

        return f"{hour}:{minute}"


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
