import ephem
from datetime import datetime, timedelta
import pytz  # Библиотека для работы с часовыми поясами

# Настройки
OBSERVER_LAT = '40.7128'  # Широта Нью-Йорка
OBSERVER_LON = '-74.0060'  # Долгота
NY_TZ = pytz.timezone('America/New_York')  # Часовой пояс NY
ORB = 2  # Допуск в градусах
ASPECTS = {0: "Conjunction", 90: "Square", 180: "Opposition"}

def get_planet_pos(planet, observer):
    if planet == "Sun":
        return ephem.Sun(observer).ra / ephem.degree
    elif planet == "Moon":
        return ephem.Moon(observer).ra / ephem.degree
    elif planet == "Asc":
        observer.pressure = 0
        observer.horizon = '-0:34'
        return observer.radec_of(0, 0)[0] / ephem.degree % 360
    elif planet == "MC":
        return observer.sidereal_time() * 15 / ephem.degree % 360
    elif planet == "DS":
        return (get_planet_pos("Asc", observer) + 180) % 360
    elif planet == "IC":
        return (get_planet_pos("IC", observer) + 180) % 360 
    return 0

def check_aspects(date, observer):
    planets = {
        "Sun": get_planet_pos("Sun", observer),
        "Moon": get_planet_pos("Moon", observer),
        "Asc": get_planet_pos("Asc", observer),
        "MC": get_planet_pos("MC", observer),
        "DS": get_planet_pos("DS", observer),
        "IC": get_planet_pos("DS", observer)
    }

    results = []
    pairs = [
        ("Sun", "Moon"), ("Sun", "Asc"), ("Sun", "MC"), ("Sun", "DS"), ("Sun", "IC"),
        ("Moon", "Asc"), ("Moon", "MC"), ("Moon", "DS"), ("Moon", "IC")]

    for p1, p2 in pairs:
        angle = abs(planets[p1] - planets[p2]) % 360
        for aspect_angle, name in ASPECTS.items():
            if abs(angle - aspect_angle) <= ORB:
                results.append(
                    f"{date.strftime('%H:%M')}: {name} {p1}-{p2} ({angle:.1f}°)"
                )
    return results

# Устанавливаем свою дату (год, месяц, день)
custom_date = datetime(2025, 7, 4)  # ← Здесь укажите нужную дату
ny_time = NY_TZ.localize(custom_date.replace(hour=0, minute=0, second=0))

# Инициализация наблюдателя
observer = ephem.Observer()
observer.lat, observer.lon = OBSERVER_LAT, OBSERVER_LON

print(f"Анализ аспектов для NYSE ({ny_time.strftime('%Y-%m-%d %H:%M')} NY Time):")
for minute in range(0, 990, 5):  # 6.5 часов, шаг 5 минут
    current_date = ny_time + timedelta(minutes=minute)
    observer.date = current_date
    aspects = check_aspects(current_date, observer)
    if aspects:
        print(f"\n{current_date.strftime('%H:%M')}:")
        print("\n".join(aspects))
