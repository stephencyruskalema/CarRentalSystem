from django.urls import path
from . import views

urlpatterns = [
    #Home
    path('', views.home, name='home'),

    #Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    #Customer - Cars
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),

    #Customer - Bookings
    path('cars/<int:pk>/book/', views.book_car, name='book_car'),
    path('bookings/', views.booking_history, name='booking_history'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),

    #Admin Dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-panel/bookings/<int:pk>/approve/', views.approve_booking, name='approve_booking'),
    path('admin-panel/bookings/<int:pk>/cancel/', views.cancel_booking_admin, name='cancel_booking_admin'),

    #Admin - Car CRUD
    path('admin-panel/cars/', views.admin_cars, name='admin_cars'),
    path('admin-panel/cars/add/', views.car_create, name='car_create'),
    path('admin-panel/cars/<int:pk>/edit/', views.car_update, name='car_update'),
    path('admin-panel/cars/<int:pk>/delete/', views.car_delete, name='car_delete'),

    #Contact/Feedback
    path('contact/', views.contact, name='contact'),
    path('admin-panel/feedback/', views.admin_feedback, name='admin_feedback'),
]
