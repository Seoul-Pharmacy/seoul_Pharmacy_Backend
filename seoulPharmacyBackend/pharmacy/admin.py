from django.contrib import admin

from pharmacy.models import Pharmacy


# Register your models here.

class PharmacyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gu', 'road_name_address']
    list_filter = ['gu', 'speaking_english', 'speaking_japanese', 'speaking_chinese']
    search_fields = ['name', 'gu', 'road_name_address']

    # def changelist_view(self, request, extra_context=None):
    #     if (extra_context is None):
    #         extra_context = {}
    #     extra_context.update({'buttons': [
    #         {'name': '약국 운영 시간 전체 업데이트', 'url': '/api/pharmacies/hours'},
    #         {'name': '약국 외국어 전체 업데이트', 'url': '/api/pharmacies/languages'},
    #     ]})
    #     return super().changelist_view(request, extra_context)


admin.site.register(Pharmacy, PharmacyAdmin)
