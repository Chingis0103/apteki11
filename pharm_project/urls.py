from django.contrib import admin
from django.urls import path, include
from django.contrib.admin.models import LogEntry

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

# Настройка заголовков админки
admin.site.site_header = 'Администрирование ИС «Аптеки 11»'
admin.site.site_title = 'Аптеки 11 — админ-панель'
admin.site.index_title = 'Управление данными системы'