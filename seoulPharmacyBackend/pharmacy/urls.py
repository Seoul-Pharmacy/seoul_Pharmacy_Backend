from django.urls import path

from pharmacy import views

urlpatterns = [
    path('pharmacies', views.pharmacy_list),
    path('nearby-pharmacies', views.nearby_pharmacy_list),
    path('pharmacies/hours', views.pharmacies_hours_update),
    path('pharmacies/languages', views.pharmacies_languages_update),
    path('pharmacies/<int:id>', views.PharmacyDetails.as_view()),
]
