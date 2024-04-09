from django.db import models


class Pharmacy(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False)

    si = models.CharField(max_length=10, blank=False, null=False)
    gu = models.CharField(max_length=10, blank=False, null=False)
    roadNameAddress = models.CharField(max_length=100, blank=False, null=False)

    main_number = models.CharField(max_length=13)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=False, null=False)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=False, null=False)

    speaking_english = models.BooleanField(null=False)
    speaking_japanese = models.BooleanField(null=False)
    speaking_chinese = models.BooleanField(null=False)

    mon_open_time = models.TimeField
    tue_open_time = models.TimeField
    wed_open_time = models.TimeField
    thu_open_time = models.TimeField
    fri_open_time = models.TimeField
    sat_open_time = models.TimeField
    sun_open_time = models.TimeField
    holiday_open_time = models.TimeField

    mon_close_time = models.TimeField
    tue_close_time = models.TimeField
    wed_close_time = models.TimeField
    thu_close_time = models.TimeField
    fri_close_time = models.TimeField
    sat_close_time = models.TimeField
    sun_close_time = models.TimeField
    holiday_close_time = models.TimeField

