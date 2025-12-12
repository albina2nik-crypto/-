from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from datetime import date, timedelta
import uuid

from .forms import CustomUserCreationForm, BookingForm
from .models import Booking, Room

# --- General Views ---

class HomeView(TemplateView):
    template_name = 'hotel/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today().isoformat()
        context['tomorrow'] = (date.today() + timedelta(days=1)).isoformat()
        return context

class AboutView(TemplateView):
    template_name = 'hotel/about.html'

class ContactView(TemplateView):
    template_name = 'hotel/contact.html'

# --- User Authentication Views ---

class CustomRegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'hotel/register.html'

    def form_valid(self, form):
        messages.success(self.request, 'Регистрация прошла успешно! Теперь вы можете войти.')
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'hotel/login.html'
    
    def form_valid(self, form):
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)

# --- User Profile Views ---

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'hotel/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings'] = Booking.objects.filter(user=self.request.user).order_by('-check_in_date')
        return context

# --- Room Views ---

class RoomListView(TemplateView):
    template_name = 'hotel/room_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        room_type = self.request.GET.get('room_type')
        max_guests = self.request.GET.get('max_guests')
        
        rooms = Room.objects.all()
        
        if check_in and check_out:
            try:
                check_in_date = date.fromisoformat(check_in)
                check_out_date = date.fromisoformat(check_out)
                
                booked_rooms_ids = Booking.objects.filter(
                    Q(status='paid') | Q(status='pending'),
                    check_in_date__lt=check_out_date,
                    check_out_date__gt=check_in_date
                ).values_list('room_id', flat=True).distinct()
                
                rooms = rooms.exclude(id__in=booked_rooms_ids)
                
                context['check_in'] = check_in
                context['check_out'] = check_out
                context['is_filtered'] = True
                
            except ValueError:
                messages.error(self.request, 'Неверный формат даты.')
        
        if room_type and room_type != 'all':
            rooms = rooms.filter(room_type=room_type)
            context['room_type'] = room_type
            context['is_filtered'] = True
            
        if max_guests and max_guests.isdigit():
            rooms = rooms.filter(max_guests__gte=int(max_guests))
            context['max_guests'] = max_guests
            context['is_filtered'] = True
            
        context['rooms'] = rooms
        context['room_types'] = Room.ROOM_TYPES
        context['today'] = date.today().isoformat()
        context['tomorrow'] = (date.today() + timedelta(days=1)).isoformat()
        
        return context

class RoomDetailView(TemplateView):
    template_name = 'hotel/room_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = get_object_or_404(Room, pk=self.kwargs['pk'])
        context['room'] = room
        
        today = date.today()
        seven_days_later = today + timedelta(days=7)
        
        is_available = not Booking.objects.filter(
            Q(status='paid') | Q(status='pending'),
            room=room,
            check_in_date__lt=seven_days_later,
            check_out_date__gt=today
        ).exists()
        
        context['is_available'] = is_available
        context['default_check_in'] = today.isoformat()
        context['default_check_out'] = seven_days_later.isoformat()
        
        return context

# --- Booking Views ---

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'hotel/booking_create.html'

    def get_success_url(self):
        return reverse('booking_confirm', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = get_object_or_404(Room, pk=self.kwargs['room_id'])
        
        # Pre-fill dates from URL if available
        if 'check_in' in self.request.GET:
            context['form'].fields['check_in_date'].initial = self.request.GET.get('check_in')
        if 'check_out' in self.request.GET:
            context['form'].fields['check_out_date'].initial = self.request.GET.get('check_out')
            
        return context

    def form_valid(self, form):
        room = get_object_or_404(Room, pk=self.kwargs['room_id'])
        check_in = form.cleaned_data['check_in_date']
        check_out = form.cleaned_data['check_out_date']

        # Final availability check before saving
        conflicting_bookings = Booking.objects.filter(
            room=room,
            status__in=['pending', 'paid'],
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        ).exists()

        if conflicting_bookings:
            messages.error(self.request, 'К сожалению, этот номер уже забронирован на выбранные даты.')
            return self.form_invalid(form)

        form.instance.user = self.request.user
        form.instance.room = room
        
        # Calculate total price
        duration = (check_out - check_in).days
        form.instance.total_price = room.price_per_night * duration
        
        messages.success(self.request, 'Бронирование создано. Пожалуйста, подтвердите детали и перейдите к оплате.')
        return super().form_valid(form)

class PaymentMockView(LoginRequiredMixin, TemplateView):
    template_name = 'hotel/payment_mock.html'

    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['booking_id'], user=request.user)
        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, 'Не выбран способ оплаты.')
            return redirect('booking_confirm', pk=booking.pk)

        if booking.status == 'paid':
            messages.info(request, 'Бронирование уже оплачено.')
            return redirect('profile')

        # --- Payment Simulation Logic ---
        
        # 1. Create a unique transaction ID (mock)
        transaction_id = f"MOCK-{payment_method.upper()}-{uuid.uuid4().hex[:10]}"

        # 2. Create Payment object
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            transaction_id=transaction_id,
            payment_method=payment_method,
            status='completed' # Simulate successful payment
        )

        # 3. Update Booking status
        booking.status = 'paid'
        booking.save()

        messages.success(request, f'Оплата через {payment.get_payment_method_display()} прошла успешно! Бронирование подтверждено.')
        return redirect('payment_success', pk=payment.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = get_object_or_404(Booking, pk=self.kwargs['booking_id'], user=self.request.user)
        return context

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'hotel/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = get_object_or_404(Payment, pk=self.kwargs['pk'], booking__user=self.request.user)
        context['payment'] = payment
        context['booking'] = payment.booking
        return context

class BookingConfirmView(LoginRequiredMixin, TemplateView):
    template_name = 'hotel/booking_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'], user=self.request.user)
        context['booking'] = booking
        return context
