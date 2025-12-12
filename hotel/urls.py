from django.urls import path
from .views import (
    HomeView, AboutView, ContactView, 
    CustomRegisterView, CustomLoginView, CustomLogoutView, 
    ProfileView, RoomListView, RoomDetailView,
    BookingCreateView, BookingConfirmView, PaymentMockView, PaymentSuccessView
)

urlpatterns = [
    # General Pages
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    
    # Authentication
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Rooms (Placeholder)
    path('rooms/', RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room_detail'),
    
    # Booking
    path('rooms/<int:room_id>/book/', BookingCreateView.as_view(), name='booking_create'),
    path('booking/<int:pk>/confirm/', BookingConfirmView.as_view(), name='booking_confirm'),
    path('payment/<int:booking_id>/mock/', PaymentMockView.as_view(), name='payment_mock'),
    path('payment/<int:pk>/success/', PaymentSuccessView.as_view(), name='payment_success'),
]
