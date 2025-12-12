from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from hotel.models import Room, Employee, Booking
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data for rooms, employees, and bookings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Запуск заполнения базы данных демоданными ---'))

        # 1. Create Superuser (if not exists)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hotel.kz', 'adminpassword')
            self.stdout.write(self.style.SUCCESS('Создан суперпользователь: admin/adminpassword'))
        
        # 2. Create Regular User (if not exists)
        if not User.objects.filter(username='user').exists():
            User.objects.create_user('user', 'user@test.kz', 'userpassword', phone_number='77071234567')
            self.stdout.write(self.style.SUCCESS('Создан тестовый пользователь: user/userpassword'))

        # 3. Create Employees (4-6)
        Employee.objects.all().delete()
        employees_data = [
            {'full_name': 'Айжан Каримова', 'position': 'Администратор', 'access_level': 'admin', 'email': 'a.karimova@hotel.kz', 'phone_number': '77011111111', 'start_date': date(2020, 1, 15)},
            {'full_name': 'Бауыржан Султанов', 'position': 'Менеджер', 'access_level': 'manager', 'email': 'b.sultanov@hotel.kz', 'phone_number': '77022222222', 'start_date': date(2021, 5, 20)},
            {'full_name': 'Сауле Ибраева', 'position': 'Ресепшн', 'access_level': 'reception', 'email': 's.ibraeva@hotel.kz', 'phone_number': '77033333333', 'start_date': date(2022, 10, 1)},
            {'full_name': 'Данияр Ахметов', 'position': 'Ресепшн', 'access_level': 'reception', 'email': 'd.akhmetov@hotel.kz', 'phone_number': '77044444444', 'start_date': date(2023, 3, 10)},
            {'full_name': 'Ерлан Жолдасбеков', 'position': 'Менеджер', 'access_level': 'manager', 'email': 'e.zholdasbekov@hotel.kz', 'phone_number': '77055555555', 'start_date': date(2024, 1, 1)},
        ]
        employees = [Employee(**data) for data in employees_data]
        Employee.objects.bulk_create(employees)
        self.stdout.write(self.style.SUCCESS(f'Создано {len(employees)} сотрудников.'))
        
        # 4. Create Rooms (10-12)
        Room.objects.all().delete()
        rooms_data = [
            # Single
            {'number': '101', 'room_type': 'single', 'price_per_night': 15000, 'max_guests': 1, 'description': 'Уютный одноместный номер с видом во двор.', 'amenities': 'Wi-Fi, ТВ, Душ'},
            {'number': '102', 'room_type': 'single', 'price_per_night': 16000, 'max_guests': 1, 'description': 'Улучшенный одноместный номер с балконом.', 'amenities': 'Wi-Fi, ТВ, Душ, Балкон'},
            # Double
            {'number': '201', 'room_type': 'double', 'price_per_night': 22000, 'max_guests': 2, 'description': 'Стандартный двухместный номер с двумя раздельными кроватями.', 'amenities': 'Wi-Fi, ТВ, Ванна, Мини-бар'},
            {'number': '202', 'room_type': 'double', 'price_per_night': 25000, 'max_guests': 2, 'description': 'Двухместный номер с большой кроватью и рабочим столом.', 'amenities': 'Wi-Fi, ТВ, Ванна, Мини-бар, Кондиционер'},
            {'number': '203', 'room_type': 'double', 'price_per_night': 24000, 'max_guests': 3, 'description': 'Просторный двухместный номер с возможностью установки дополнительной кровати.', 'amenities': 'Wi-Fi, ТВ, Ванна, Мини-бар, Кондиционер'},
            # Suite
            {'number': '301', 'room_type': 'suite', 'price_per_night': 45000, 'max_guests': 4, 'description': 'Роскошный люкс с отдельной гостиной и панорамным видом.', 'amenities': 'Wi-Fi, 2 ТВ, Джакузи, Мини-бар, Кондиционер, Завтрак включен'},
            {'number': '302', 'room_type': 'suite', 'price_per_night': 40000, 'max_guests': 2, 'description': 'Малый люкс для двоих с повышенным комфортом.', 'amenities': 'Wi-Fi, ТВ, Ванна, Мини-бар, Кондиционер'},
            # Family
            {'number': '401', 'room_type': 'family', 'price_per_night': 35000, 'max_guests': 5, 'description': 'Семейный номер с двумя спальнями и общей гостиной.', 'amenities': 'Wi-Fi, 2 ТВ, Кухня, Ванна, Кондиционер'},
            {'number': '402', 'room_type': 'family', 'price_per_night': 32000, 'max_guests': 4, 'description': 'Большой семейный номер с видом на город.', 'amenities': 'Wi-Fi, ТВ, Ванна, Кондиционер'},
            # Double (more)
            {'number': '501', 'room_type': 'double', 'price_per_night': 20000, 'max_guests': 2, 'description': 'Тихий двухместный номер на верхнем этаже.', 'amenities': 'Wi-Fi, ТВ, Душ'},
            {'number': '502', 'room_type': 'double', 'price_per_night': 21000, 'max_guests': 2, 'description': 'Двухместный номер с видом на бассейн.', 'amenities': 'Wi-Fi, ТВ, Душ, Балкон'},
        ]
        rooms = [Room(**data) for data in rooms_data]
        Room.objects.bulk_create(rooms)
        self.stdout.write(self.style.SUCCESS(f'Создано {len(rooms)} номеров.'))

        # 5. Create Bookings (Demo)
        Booking.objects.all().delete()
        test_user = User.objects.get(username='user')
        admin_employee = Employee.objects.get(access_level='admin')
        
        today = date.today()
        
        bookings_data = [
            # Past Paid Booking
            {'user': test_user, 'room': rooms[0], 'check_in_date': today - timedelta(days=10), 'check_out_date': today - timedelta(days=5), 'guests': 1, 'status': 'paid', 'total_price': rooms[0].price_per_night * 5, 'processed_by': admin_employee},
            # Current Paid Booking (Occupied)
            {'user': test_user, 'room': rooms[1], 'check_in_date': today - timedelta(days=2), 'check_out_date': today + timedelta(days=3), 'guests': 1, 'status': 'paid', 'total_price': rooms[1].price_per_night * 5, 'processed_by': admin_employee},
            # Future Pending Booking (Occupied)
            {'user': test_user, 'room': rooms[2], 'check_in_date': today + timedelta(days=7), 'check_out_date': today + timedelta(days=10), 'guests': 2, 'status': 'pending', 'total_price': rooms[2].price_per_night * 3, 'processed_by': admin_employee},
            # Future Paid Booking
            {'user': test_user, 'room': rooms[3], 'check_in_date': today + timedelta(days=15), 'check_out_date': today + timedelta(days=17), 'guests': 2, 'status': 'paid', 'total_price': rooms[3].price_per_night * 2, 'processed_by': admin_employee},
            # Future Cancelled Booking
            {'user': test_user, 'room': rooms[4], 'check_in_date': today + timedelta(days=20), 'check_out_date': today + timedelta(days=22), 'guests': 3, 'status': 'cancelled', 'total_price': rooms[4].price_per_night * 2, 'processed_by': admin_employee},
        ]
        
        bookings = [Booking(**data) for data in bookings_data]
        Booking.objects.bulk_create(bookings)
        self.stdout.write(self.style.SUCCESS(f'Создано {len(bookings)} демо-бронирований.'))

        self.stdout.write(self.style.SUCCESS('--- Заполнение базы данных завершено ---'))
