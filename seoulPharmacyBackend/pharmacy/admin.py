from django.contrib import admin

from pharmacy.models import Pharmacy


# Register your models here.

class PharmacyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Pharmacy, PharmacyAdmin)
