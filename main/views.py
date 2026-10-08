from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, ProfileForm, ReservationForm
from django.contrib import messages
from django.db.models import Q
from .models import Pharmacy, Medicine, Stock, Reservation


def index(request):
    """Главная: карта аптек + краткая статистика."""
    pharmacies = Pharmacy.objects.filter(is_active=True)
    stats = {
        'pharmacies': pharmacies.count(),
        'medicines': Medicine.objects.count(),
        'inns': Medicine.objects.values('inn').distinct().count(),
    }

    # Явно преобразуем в список словарей — только нужные поля для карты
    pharmacies_data = list(
        pharmacies.values('id', 'name', 'address', 'latitude', 'longitude', 'phone', 'is_24h')
    )

    return render(request, 'main/index.html', {
        'pharmacies': pharmacies,
        'pharmacies_data': pharmacies_data,   # ← новое
        'stats': stats,
    })


def pharmacy_list(request):
    """Список аптек (без карты, просто таблица/карточки)."""
    pharmacies = Pharmacy.objects.filter(is_active=True)
    return render(request, 'main/pharmacies.html', {
        'pharmacies': pharmacies,
    })


def search(request):
    """Поиск лекарств по торговому названию или МНН."""
    query = request.GET.get('q', '').strip()
    medicines = Medicine.objects.none()

    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) |
            Q(inn__name_ru__icontains=query) |
            Q(inn__name_lat__icontains=query)
        ).select_related('inn').distinct()

    return render(request, 'main/search.html', {
        'query': query,
        'medicines': medicines,
    })


def medicine_detail(request, pk):
    """Страница лекарства: аналоги + наличие в аптеках."""
    medicine = get_object_or_404(Medicine.objects.select_related('inn'), pk=pk)
    analogs = medicine.get_analogs()
    stocks = Stock.objects.filter(
        medicine=medicine,
        quantity__gt=0,
        pharmacy__is_active=True,
    ).select_related('pharmacy').order_by('price')

    return render(request, 'main/medicine_detail.html', {
        'medicine': medicine,
        'analogs': analogs,
        'stocks': stocks,
    })


def register(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('main:index')
    else:
        form = RegisterForm()

    return render(request, 'main/register.html', {'form': form})


def login_view(request):
    """Вход в систему."""
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, 'Вы вошли в систему.')
            # Редирект туда, откуда пришёл (если есть ?next=)
            next_url = request.GET.get('next') or 'main:index'
            return redirect(next_url)
    else:
        form = LoginForm(request)

    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    """Выход из системы."""
    auth_logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('main:index')


@login_required
def profile(request):
    """Личный кабинет."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('main:profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    reservations = request.user.reservations.all()[:10]

    return render(request, 'main/profile.html', {
        'form': form,
        'reservations': reservations,
    })


from django.utils import timezone
from .forms import ReservationForm


# Максимум активных броней у одного пользователя
MAX_ACTIVE_RESERVATIONS = 5


@login_required
def reserve(request, stock_id):
    """Создание брони на конкретную позицию наличия."""
    stock = get_object_or_404(
        Stock.objects.select_related('pharmacy', 'medicine'),
        pk=stock_id
    )

    # Проверка: есть ли в наличии
    if stock.quantity <= 0:
        messages.error(request, 'Этого лекарства нет в наличии.')
        return redirect('main:medicine_detail', pk=stock.medicine.pk)

    # Проверка: не превышен ли лимит активных броней
    active_count = request.user.reservations.filter(
        status__in=['new', 'confirmed']
    ).count()
    if active_count >= MAX_ACTIVE_RESERVATIONS:
        messages.error(
            request,
            f'У вас уже {MAX_ACTIVE_RESERVATIONS} активных броней. '
            f'Дождитесь их обработки или отмените старые.'
        )
        return redirect('main:profile')

    if request.method == 'POST':
        form = ReservationForm(request.POST, stock=stock)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.stock = stock
            reservation.status = 'new'
            reservation.save()
            messages.success(
                request,
                f'Заявка #{reservation.pk} создана. '
                f'Аптека «{stock.pharmacy.name}» свяжется с вами.'
            )
            return redirect('main:profile')
    else:
        form = ReservationForm(stock=stock)

    return render(request, 'main/reserve_form.html', {
        'form': form,
        'stock': stock,
    })


@login_required
def my_reservations(request):
    """Мои бронирования с фильтром по статусу."""
    status_filter = request.GET.get('status', '')
    reservations = request.user.reservations.select_related(
        'stock__medicine', 'stock__pharmacy'
    )

    if status_filter and status_filter in dict(Reservation.STATUS_CHOICES):
        reservations = reservations.filter(status=status_filter)

    return render(request, 'main/my_reservations.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'statuses': Reservation.STATUS_CHOICES,
    })


@login_required
def cancel_reservation(request, pk):
    """Отмена своей брони (только new или confirmed)."""
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if reservation.status not in ('new', 'confirmed'):
        messages.error(request, 'Эту бронь нельзя отменить.')
        return redirect('main:my_reservations')

    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.info(request, f'Бронь #{reservation.pk} отменена.')
        return redirect('main:my_reservations')

    return render(request, 'main/cancel_reservation.html', {
        'reservation': reservation,
    })


@login_required
def pharmacist_panel(request):
    """Панель фармацевта: заявки в его аптеке."""
    profile = request.user.profile

    if profile.role != 'pharmacist' or not profile.pharmacy:
        messages.error(request, 'Доступ только для фармацевтов с привязанной аптекой.')
        return redirect('main:index')

    # Фильтр по статусу
    status_filter = request.GET.get('status', '')
    reservations = Reservation.objects.filter(
        stock__pharmacy=profile.pharmacy
    ).select_related('user', 'stock__medicine').order_by('-created_at')

    if status_filter and status_filter in dict(Reservation.STATUS_CHOICES):
        reservations = reservations.filter(status=status_filter)

    # Обработка смены статуса
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        new_status = request.POST.get('new_status')
        reservation = get_object_or_404(
            Reservation, pk=reservation_id, stock__pharmacy=profile.pharmacy
        )
        if new_status in dict(Reservation.STATUS_CHOICES):
            reservation.status = new_status
            reservation.save()
            messages.success(
                request,
                f'Статус заявки #{reservation.pk} изменён на '
                f'«{reservation.get_status_display()}».'
            )
        return redirect('main:pharmacist_panel')

    return render(request, 'main/pharmacist_panel.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'statuses': Reservation.STATUS_CHOICES,
        'pharmacy': profile.pharmacy,
    })