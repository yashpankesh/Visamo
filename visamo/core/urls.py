from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.profile, name='profile'),
    path('about/', views.about_us, name='about_us'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book_hotel/<int:hotel_id>/', views.book_hotel, name='book_hotel'),
    path('process_payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
]


