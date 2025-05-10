from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product-description/<str:product_name>/', views.product_description_view, name='product_description'),
    path('filter_by_category/<str:category>/', views.home, name='filter_by_category'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('clear-orders/', views.clear_orders, name='clear_orders'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('make-payment/<int:order_id>/', views.make_payment, name='make_payment'),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),
    path('product-description/<str:product_name>/add_comment/', views.add_comment, name='add_comment'),
]