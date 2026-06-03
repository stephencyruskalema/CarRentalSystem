from django.contrib import admin
from .models import UserProfile, Car, Booking, Feedback

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'year', 'category', 'license_plate', 'daily_price', 'status']
    list_filter = ['category', 'status']
    search_fields = ['make', 'model', 'license_plate']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'car', 'start_date', 'end_date', 'total_price', 'status']
    list_filter = ['status']
    search_fields = ['user__username', 'car__make']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read']