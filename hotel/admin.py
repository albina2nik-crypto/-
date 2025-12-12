from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Employee, Room, Booking, Payment

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (('Дополнительная информация'), {'fields': ('phone_number',)}),
    )

# Employee Admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'access_level', 'email', 'phone_number', 'start_date']
    list_filter = ['access_level', 'position']
    search_fields = ['full_name', 'email', 'phone_number']

# Room Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'room_type', 'price_per_night', 'max_guests']
    list_filter = ['room_type', 'max_guests']
    search_fields = ['number', 'description']
    list_editable = ['price_per_night', 'max_guests']

# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'room', 'check_in_date', 'check_out_date', 'total_price', 'status', 'processed_by']
    list_filter = ['status', 'check_in_date', 'check_out_date', 'room__room_type']
    search_fields = ['user__username', 'room__number']
    raw_id_fields = ['user', 'room', 'processed_by']
    actions = ['mark_paid', 'mark_cancelled']

    @admin.action(description='Отметить выбранные брони как Оплаченные')
    def mark_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} бронирований отмечены как оплаченные.')

    @admin.action(description='Отметить выбранные брони как Отмененные')
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} бронирований отмечены как отмененные.')

# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'payment_method', 'status', 'timestamp', 'transaction_id']
    list_filter = ['status', 'payment_method']
    search_fields = ['transaction_id', 'booking__id']
    raw_id_fields = ['booking']

# Register Custom User
admin.site.register(CustomUser, CustomUserAdmin)

# Change admin site titles
admin.site.site_header = "Администрирование Hotel Booking System"
admin.site.site_title = "Hotel Booking System Admin"
admin.site.index_title = "Добро пожаловать в панель управления отелем"
