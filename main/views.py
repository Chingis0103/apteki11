from django.shortcuts import render, get_object_or_404
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