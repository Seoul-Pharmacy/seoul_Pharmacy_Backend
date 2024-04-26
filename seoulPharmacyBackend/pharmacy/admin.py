from django.contrib import admin

from pharmacy.models import Pharmacy


# Register your models here.

class PharmacyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gu', 'road_name_address']
    list_filter = ['name', 'gu', 'speaking_english', 'speaking_japanese', 'speaking_chinese']
    search_fields = ['name', 'gu', 'road_name_address']


admin.site.register(Pharmacy, PharmacyAdmin)
