from django.contrib import admin
from django.urls import path
from base import views

urlpatterns = [
    path('registration/', views.user_registration, name='user_registration'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('authcheck/', views.authcheck, name='authcheck'),
    path('send_mail_to_reset_password/', views.send_mail_to_reset_password, name='send_mail_to_reset_password'),
    path('reset_password_view/', views.reset_password_view, name='reset_password_view'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('update_user_details/', views.update_user_details, name='update_user_details'),
]
