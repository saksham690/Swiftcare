from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('About_Us',views.About_Us,name='About_Us'),
    path('Contact_Us',views.Contact_us,name='Contact_Us'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('searchbar/', views.searchbar, name='searchbar'),
    path('doctordes/<int:doctor_id>/', views.doctordes, name='doctordes'),
    path('patient_page/', views.patient_page, name='patient_page'),
    path('doclog/', views.doclog, name='doclog'),
    path('request_appointment/', views.request_appointment, name='request_appointment'),
    path('update_appointment/<int:appointment_id>/', views.update_appointment, name='update_appointment'),
    path('response/', views.response_view, name='response'),
    path('user_appointments/', views.user_appointments, name='user_appointments'),
    path('register_doctor/', views.register_doctor, name='register_doctor'),
    path('doctor_login/', views.doctor_login, name='doctor_login'),
    path('doctor_book/', views.doctor_book, name='doctor_book'),
    path('doctor_logout/', views.doctor_logout, name='doctor_logout'),
    path('send_otp/<str:user_type>/', views.send_otp, name='send_otp'),
    path('verify_otp/<str:user_type>/', views.verify_otp, name='verify_otp'),
    path('lab_reports/', views.lab_reports, name='lab_reports')
]