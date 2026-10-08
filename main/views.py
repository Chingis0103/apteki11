from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, ProfileForm
from django.contrib import messages
from django.db.models import Q
from .models import Pharmacy, Medicine, Stock


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