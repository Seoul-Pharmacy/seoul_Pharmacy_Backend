from django.urls import path

from pharmacy import views

urlpatterns = [
    path('pharmacies', views.pharmacyList),
    path('pharmacy', views.pharmacySave),
    path('pharmacies/<int:id>', views.PharmacyDetails.as_view()),
]
