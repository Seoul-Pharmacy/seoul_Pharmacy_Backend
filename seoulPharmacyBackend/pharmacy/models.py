from django.db import models


class Pharmacy(models.Model):
    class Meta:
        unique_together = ('name', 'gu')

    id = models.AutoField(primary_key=True, db_column='pharmacy_id')

    name = models.CharField(max_length=200, blank=False, null=False)

    si = models.CharField(max_length=10, blank=False, null=False)
    gu = models.CharField(max_length=10, blank=False, null=False)
    road_name_address = models.CharField(max_length=100, blank=False, null=False)

    main_number = models.CharField(max_length=20)

    latitude = models.DecimalField(max_digits=23, decimal_places=20, blank=False, null=False)
    longitude = models.DecimalField(max_digits=23, decimal_places=20, blank=False, null=False)

    speaking_english = models.BooleanField(null=False, default=False)
    speaking_japanese = models.BooleanField(null=False, default=False)
    speaking_chinese = models.BooleanField(null=False, default=False)

    mon_open_time = models.TimeField(null=True)
    tue_open_time = models.TimeField(null=True)
    wed_open_time = models.TimeField(null=True)
    thu_open_time = models.TimeField(null=True)
    fri_open_time = models.TimeField(null=True)
    sat_open_time = models.TimeField(null=True)
    sun_open_time = models.TimeField(null=True)
    holiday_open_time = models.TimeField(null=True)

    mon_close_time = models.TimeField(null=True)
    tue_close_time = models.TimeField(null=True)
    wed_close_time = models.TimeField(null=True)
    thu_close_time = models.TimeField(null=True)
    fri_close_time = models.TimeField(null=True)
    sat_close_time = models.TimeField(null=True)
    sun_close_time = models.TimeField(null=True)
    holiday_close_time = models.TimeField(null=True)

    last_modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
