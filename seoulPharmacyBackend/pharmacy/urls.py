from django.urls import path

from pharmacy import views

urlpatterns = [
    path('pharmacies', views.pharmacy_list),
    path('pharmacy', views.pharmacy_save),
    path('pharmacies/<int:id>', views.PharmacyDetails.as_view()),
]
