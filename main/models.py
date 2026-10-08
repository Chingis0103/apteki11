from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class INN(models.Model):
    """Международное непатентованное наименование (МНН)."""
    name_ru = models.CharField('Название (рус.)', max_length=200, unique=True)
    name_lat = models.CharField('Название (лат.)', max_length=200, blank=True)
    atc_code = models.CharField('ATC-код', max_length=20, blank=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'МНН'
        verbose_name_plural = 'МНН (справочник)'
        ordering = ['name_ru']

    def __str__(self):
        return self.name_ru


class Pharmacy(models.Model):
    """Аптека."""
    name = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=300)
    latitude = models.FloatField('Широта')
    longitude = models.FloatField('Долгота')
    phone = models.CharField('Телефон', max_length=30, blank=True)
    is_24h = models.BooleanField('Круглосуточная', default=False)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Аптека'
        verbose_name_plural = 'Аптеки'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.address})'


class Medicine(models.Model):
    """Торговое наименование лекарства."""
    FORM_CHOICES = [
        ('tablets', 'Таблетки'),
        ('capsules', 'Капсулы'),
        ('solution', 'Раствор'),
        ('ointment', 'Мазь'),
        ('spray', 'Спрей'),
        ('other', 'Другое'),
    ]

    name = models.CharField('Торговое название', max_length=200, db_index=True)
    inn = models.ForeignKey(
        INN, on_delete=models.PROTECT,
        related_name='medicines', verbose_name='МНН'
    )
    form = models.CharField('Форма выпуска', max_length=20, choices=FORM_CHOICES, default='tablets')
    dosage = models.CharField('Дозировка', max_length=100, blank=True)
    is_prescription = models.BooleanField('По рецепту', default=False)
    description = models.TextField('Описание', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Лекарство'
        verbose_name_plural = 'Лекарства'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['inn']),
        ]

    def __str__(self):
        return f'{self.name} ({self.dosage})' if self.dosage else self.name

    def get_analogs(self):
        """Аналоги — лекарства с тем же МНН, кроме самого себя."""
        return Medicine.objects.filter(inn=self.inn).exclude(pk=self.pk)


class Stock(models.Model):
    """Наличие лекарства в аптеке."""
    pharmacy = models.ForeignKey(
        Pharmacy, on_delete=models.CASCADE,
        related_name='stocks', verbose_name='Аптека'
    )
    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE,
        related_name='stocks', verbose_name='Лекарство'
    )
    price = models.DecimalField('Цена, ₽', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=0)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Наличие'
        verbose_name_plural = 'Наличие'
        unique_together = ('pharmacy', 'medicine')
        ordering = ['price']

    def __str__(self):
        return f'{self.medicine.name} в {self.pharmacy.name} — {self.price} ₽'


class Reservation(models.Model):
    """Бронирование лекарства."""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('rejected', 'Отклонена'),
        ('done', 'Выдана'),
        ('cancelled', 'Отменена пользователем'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='Пользователь'
    )
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='Наличие'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='new'
    )
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} — {self.stock.medicine.name} ({self.get_status_display()})'


class Profile(models.Model):
    """Расширение пользователя: роль."""
    ROLE_CHOICES = [
        ('resident', 'Житель'),
        ('pharmacist', 'Фармацевт'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='Пользователь'
    )
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='resident')
    pharmacy = models.ForeignKey(
        Pharmacy, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pharmacists', verbose_name='Аптека (для фармацевта)'
    )
    phone = models.CharField('Телефон', max_length=30, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'{self.user.username} — {self.get_role_display()}'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Автоматически создаём профиль при регистрации пользователя."""
    if created:
        Profile.objects.create(user=instance)