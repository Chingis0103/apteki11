# Аптеки 11

Информационная система поиска лекарств и бронирования в аптеках Республики Коми.

[![Django](https://img.shields.io/badge/Django-6.1.2-green)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](#)

## 📌 О проекте

«Аптеки 11» — веб-приложение для жителей и гостей Республики Коми, позволяющее:

- 🗺️ **Находить аптеки** на интерактивной карте
- 💊 **Искать лекарства** по торговому названию или МНН
- 🔄 **Подбирать аналоги** по международному непатентованному наименованию
- 📋 **Бронировать лекарства** в выбранной аптеке
- 👨‍⚕️ **Управлять наличием** (для фармацевтов)

## 🛠️ Стек технологий

| Слой | Технология |
|------|-----------|
| **Backend** | Python 3.14, Django 6.1 |
| **База данных** | PostgreSQL 18 (локально) / SQLite (на сервере) |
| **Frontend** | Django Templates, Bootstrap 5, JavaScript (fetch API) |
| **Карта** | MapLibre GL JS + OpenFreeMap (бесплатные тайлы) |
| **Хранение секретов** | python-decouple, python-dotenv |
| **Статика** | WhiteNoise |
| **Версионирование** | Git + GitHub |
| **Хостинг** | PythonAnywhere |

## 📂 Структура проекта

apteki11/
├── main/ # Основное приложение
│ ├── fixtures/
│ │ └── initial_data.json # Фикстура: 10 аптек, 17 лекарств
│ ├── management/commands/
│ │ └── create_demo_users.py # Создание демо-пользователей
│ ├── migrations/ # Миграции БД
│ ├── templates/main/ # HTML-шаблоны
│ ├── admin.py # Настройка админки
│ ├── forms.py # Формы (регистрация, бронирование, наличие)
│ ├── models.py # Модели: INN, Pharmacy, Medicine, Stock, Reservation, Profile
│ ├── urls.py # Маршруты приложения
│ └── views.py # Представления
├── pharm_project/ # Настройки Django
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── static/css/style.css # Стили
├── .env.example # Шаблон переменных окружения
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt

## 🏗️ Модели данных

- **INN** — справочник МНН (международных непатентованных наименований)
- **Medicine** — торговые названия лекарств (привязаны к МНН)
- **Pharmacy** — аптеки с координатами для карты
- **Stock** — наличие лекарств в аптеках (цена, количество)
- **Reservation** — бронирования жителей
- **Profile** — расширение пользователя (роль: житель / фармацевт / админ)

## ⚙️ Установка локально

### 1. Клонирование

```bash
git clone https://github.com/Chingis0103/apteki11.git
cd apteki11

2. Виртуальное окружение
Windows:

cmd
python -m venv venv
venv\Scripts\activate.bat

Linux / macOS:

bash
python3 -m venv venv
source venv/bin/activate

3. Зависимости
bash
pip install -r requirements.txt
4. Переменные окружения
Скопируй .env.example в .env и заполни:

bash
cp .env.example .env
Содержимое .env:

text
SECRET_KEY=сгенерируй-свой-ключ
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=apteki11
DB_USER=postgres
DB_PASSWORD=твой_пароль
DB_HOST=127.0.0.1
DB_PORT=5432
Генерация SECRET_KEY:

bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
5. База данных
Создай базу в PostgreSQL:

sql
CREATE DATABASE apteki11 WITH ENCODING 'UTF8';
Примени миграции:

bash
python manage.py migrate
6. Загрузка данных
bash
python manage.py loaddata main/fixtures/initial_data.json
python manage.py create_demo_users
7. Суперпользователь
bash
python manage.py createsuperuser
8. Запуск
bash
python manage.py runserver
Открой http://127.0.0.1:8000

🚢 Деплой на PythonAnywhere
Краткая шпаргалка:

bash
# 1. Клонировать репозиторий
git clone https://github.com/Chingis0103/apteki11.git
cd apteki11

# 2. Создать виртуальное окружение (Python 3.12)
mkvirtualenv --python=/usr/bin/python3.12 venv

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env (DEBUG=False, ALLOWED_HOSTS=username.pythonanywhere.com)

# 5. Миграции, фикстура, демо-юзеры
python manage.py migrate
python manage.py loaddata main/fixtures/initial_data.json
python manage.py create_demo_users
python manage.py collectstatic --noinput
Подробнее — в Руководстве администратора.

🧪 Тесты
bash
python manage.py test

📝 Особенности
SQLite на сервере — icontains не работает с кириллицей (регистрозависимый поиск). Это известное ограничение SQLite.

PostgreSQL локально — регистронезависимый поиск работает корректно.

Карта — использует OpenFreeMap (не требует API-ключей).

Лимит броней — не более 5 активных на пользователя.

👤 Автор
Евгений (Chingis0103) — студент направления 09.03.02 «Информационные системы и технологии», СЛИ, 2026.

GitHub: @Chingis0103

📄 Лицензия
Учебный проект. Свободное использование в образовательных целях.