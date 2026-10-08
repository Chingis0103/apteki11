"""
Геокодер адресов аптек через Nominatim (OpenStreetMap).
Бесплатно, без API-ключей. Лимит: 1 запрос в секунду.
Документация: https://nominatim.org/release-docs/latest/api/Search/
"""

import time
import json
import urllib.parse
import urllib.request

# Список адресов из фикстуры
ADDRESSES = [
    ("Будь Здоров!", "Сыктывкар, улица Мира, 11"),
    ("Ригла", "Сыктывкар, Октябрьский проспект, 141"),
    ("Максимум", "Сыктывкар, Интернациональная улица, 157"),
    ("Планета здоровья (Мира)", "Сыктывкар, улица Мира, 13"),
    ("Аптека от склада", "Сыктывкар, проспект Бумажников, 53"),
    ("Государственные аптеки РК", "Сыктывкар, Лесозаводская улица, 15"),
    ("Планета здоровья (Карла Маркса)", "Сыктывкар, улица Карла Маркса, 183"),
    ("Планета здоровья (Покровский)", "Сыктывкар, Покровский бульвар, 9"),
    ("Аптека №1 (ГУП РК)", "Сыктывкар, улица Ленина, 49"),
    ("Аптека 38 Плюс", "Сыктывкар, улица Ленина, 131"),
]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "Apteki11-StudentProject/1.0 (educational use)"


def geocode(query):
    """Возвращает (lat, lon) или None."""
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "ru",
    }
    url = f"{NOMINATIM_URL}?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"  ⚠️  Ошибка: {e}")
    return None


def main():
    results = []
    print("🌍 Геокодирую адреса через Nominatim...\n")

    for name, address in ADDRESSES:
        print(f"📍 {name}")
        print(f"   Адрес: {address}")

        coords = geocode(address)

        if coords:
            lat, lon = coords
            print(f"   ✅ {lat:.6f}, {lon:.6f}")
            results.append({
                "name": name,
                "address": address,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
            })
        else:
            print(f"   ❌ Не найдено")
            results.append({
                "name": name,
                "address": address,
                "latitude": None,
                "longitude": None,
            })

        print()
        time.sleep(1.1)  # Лимит Nominatim: 1 запрос в секунду

    # Сохраняем результат
    with open("geocode_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("💾 Результаты сохранены в geocode_result.json")
    print("=" * 60)

    # Итоговая таблица
    print("\n📊 ИТОГОВАЯ ТАБЛИЦА:\n")
    print(f"{'Название':<40} {'Широта':>12} {'Долгота':>12}")
    print("-" * 66)
    for r in results:
        lat = f"{r['latitude']:.6f}" if r['latitude'] else "—"
        lon = f"{r['longitude']:.6f}" if r['longitude'] else "—"
        print(f"{r['name']:<40} {lat:>12} {lon:>12}")


if __name__ == "__main__":
    main()