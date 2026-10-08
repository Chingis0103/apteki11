from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('pharmacies/', views.pharmacy_list, name='pharmacy_list'),
    path('search/', views.search, name='search'),
    path('medicine/<int:pk>/', views.medicine_detail, name='medicine_detail'),

    # Авторизация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]