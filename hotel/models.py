from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# 1. Custom User Model (for registration/authorization)
class CustomUser(AbstractUser):
    # Additional fields for registration
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("Номер телефона"))
    
    # Remove username requirement if we want to use email for login, but for simplicity, we'll keep it and add phone.
    # The 'name' field is covered by first_name/last_name in AbstractUser.
    
    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email or self.username

# 2. Employee Model
class Employee(models.Model):
    ACCESS_LEVELS = [
        ('admin', _('Администратор')),
        ('manager', _('Менеджер')),
        ('reception', _('Ресепшн')),
    ]
    
    full_name = models.CharField(max_length=255, verbose_name=_("ФИО"))
    position = models.CharField(max_length=100, verbose_name=_("Должность"))
    phone_number = models.CharField(max_length=15, verbose_name=_("Телефон"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    start_date = models.DateField(verbose_name=_("Дата начала работы"))
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='reception', verbose_name=_("Уровень доступа"))
    
    class Meta:
        verbose_name = _("Сотрудник")
        verbose_name_plural = _("Сотрудники")

    def __str__(self):
        return self.full_name

# 3. Room Model
class Room(models.Model):
    ROOM_TYPES = [
        ('single', _('Одноместный')),
        ('double', _('Двухместный')),
        ('suite', _('Люкс')),
        ('family', _('Семейный')),
    ]
    
    number = models.CharField(max_length=10, unique=True, verbose_name=_("Номер комнаты"))
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, verbose_name=_("Тип комнаты"))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена за ночь (KZT)"))
    max_guests = models.PositiveSmallIntegerField(verbose_name=_("Макс. гостей"))
    description = models.TextField(verbose_name=_("Описание"))
    amenities = models.TextField(blank=True, verbose_name=_("Удобства (через запятую)"))
    photo = models.ImageField(upload_to='room_photos/', blank=True, null=True, verbose_name=_("Фото"))
    
    class Meta:
        verbose_name = _("Комната")
        verbose_name_plural = _("Комнаты")

    def __str__(self):
        return f"Комната №{self.number} ({self.get_room_type_display()})"

# 4. Booking Model
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Ожидает')),
        ('paid', _('Оплачено')),
        ('cancelled', _('Отменено')),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings', verbose_name=_("Пользователь"))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name=_("Комната"))
    check_in_date = models.DateField(verbose_name=_("Дата заезда"))
    check_out_date = models.DateField(verbose_name=_("Дата выезда"))
    guests = models.PositiveSmallIntegerField(verbose_name=_("Количество гостей"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус брони"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Общая стоимость (KZT)"))
    
    # For admin/manager tracking
    processed_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Оформил сотрудник"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]

    def __str__(self):
        return f"Бронь №{self.id} - {self.room.number} ({self.user.username})"

# 5. Payment Model
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('kaspi', _('Kaspi Pay (Mock)')),
        ('halyk', _('Halyk Pay (Mock)')),
        ('bcc', _('BCC Pay (Mock)')),
        ('mock', _('Имитация платежа')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Ожидает')),
        ('completed', _('Завершено')),
        ('failed', _('Неуспешно')),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', verbose_name=_("Бронирование"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Сумма (KZT)"))
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name=_("ID транзакции"))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name=_("Метод оплаты"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус платежа"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата/время транзакции"))
    
    class Meta:
        verbose_name = _("Платеж")
        verbose_name_plural = _("Платежи")

    def __str__(self):
        return f"Платеж №{self.id} на сумму {self.amount} KZT ({self.get_status_display()})"
