from django.urls import path
from .views import CompareProductsAPIView

urlpatterns = [
    path("compare-products/", CompareProductsAPIView.as_view(), name="compare-products"),
]
