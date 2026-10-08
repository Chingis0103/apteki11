from django.contrib import admin
from .models import INN, Pharmacy, Medicine, Stock, Reservation, Profile


@admin.register(INN)
class INNAdmin(admin.ModelAdmin):
    list_display = ('name_ru', 'name_lat', 'atc_code')
    search_fields = ('name_ru', 'name_lat', 'atc_code')


@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_24h', 'is_active')
    list_filter = ('is_24h', 'is_active')
    search_fields = ('name', 'address')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'inn', 'form', 'dosage', 'is_prescription')
    list_filter = ('form', 'is_prescription', 'inn')
    search_fields = ('name', 'inn__name_ru')
    autocomplete_fields = ('inn',)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'pharmacy', 'price', 'quantity', 'updated_at')
    list_filter = ('pharmacy',)
    search_fields = ('medicine__name', 'pharmacy__name')
    autocomplete_fields = ('medicine', 'pharmacy')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'stock', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'stock__medicine__name')
    list_editable = ('status',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'pharmacy', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username',)