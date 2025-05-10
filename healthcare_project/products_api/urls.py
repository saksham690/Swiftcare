from django.urls import path
from .views import ProductListCreateAPIView, ProductRetrieveDestroyAPIView

urlpatterns = [
    path('', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductRetrieveDestroyAPIView.as_view(), name='product-detail'),
]
