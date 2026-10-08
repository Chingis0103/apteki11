# Аптеки 11

Учебный проект — интерактивная карта наличия лекарств в аптеках Республики Коми.

## О проекте

Сервис позволяет:
- Найти ближайшую аптеку на карте
- Проверить наличие конкретного лекарства в аптеках
- Найти аналоги по МНН (международному непатентованному наименованию)
- Забронировать лекарство в выбранной аптеке

## Стек технологий

- **Backend:** Django 6.1, Python 3.14
- **Database:** PostgreSQL 18
- **Frontend:** Django Templates, Bootstrap 5, MapLibre GL JS
- **Maps:** OpenFreeMap (бесплатные векторные тайлы)
- **DevOps:** Git, GitHub

## Установка

```bash
git clone https://github.com/Chingis0103/apteki11.git
cd apteki11
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt