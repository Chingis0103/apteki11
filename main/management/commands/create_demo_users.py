"""
Создаёт демонстрационных пользователей:
- 10 фармацевтов (по одному на каждую аптеку)
- 3 жителя

Запуск: python manage.py create_demo_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Pharmacy, Profile


class Command(BaseCommand):
    help = 'Создаёт демо-пользователей: фармацевтов и жителей'

    def handle(self, *args, **options):
        # Пароль для всех демо-пользователей
        password = 'demo12345'

        # --- Фармацевты ---
        pharmacies = Pharmacy.objects.filter(is_active=True).order_by('pk')

        for pharmacy in pharmacies:
            username = f'pharm{pharmacy.pk}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': pharmacy.name,
                    'email': f'{username}@apteki11.local',
                }
            )
            if created:
                user.set_password(password)
                user.save()

            # Обновляем профиль
            profile = user.profile
            profile.role = 'pharmacist'
            profile.pharmacy = pharmacy
            profile.phone = pharmacy.phone or ''
            profile.save()

            status = 'создан' if created else 'обновлён'
            self.stdout.write(f'  {status}: {username} → {pharmacy.name}')

        # --- Жители ---
        residents = [
            ('user1', 'Иван', 'Иванов', 'user1@example.com'),
            ('user2', 'Пётр', 'Петров', 'user2@example.com'),
            ('user3', 'Мария', 'Сидорова', 'user3@example.com'),
        ]

        for username, first_name, last_name, email in residents:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            if created:
                user.set_password(password)
                user.save()

            profile = user.profile
            profile.role = 'resident'
            profile.save()

            status = 'создан' if created else 'обновлён'
            self.stdout.write(f'  {status}: {username} → {first_name} {last_name}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Готово! Пароль для всех демо-пользователей: {password}'
        ))