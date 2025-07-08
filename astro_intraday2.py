import ephem
from datetime import datetime, timedelta
import pytz

# Настройки
OBSERVER_LAT = '40.7128'  # Широта Нью-Йорка
OBSERVER_LON = '-74.0060'  # Долгота
NY_TZ = pytz.timezone('America/New_York')
ORB = 2  # Допуск в градусах
ASPECTS = {0: "⚡", 90: "⚠", 180: "☠"}  # Символы для визуализации
STEP_MINUTES = 15  # Шаг анализа в минутах

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
        return (get_planet_pos("MC", observer) + 180) % 360 
    return 0

def check_aspects(date, observer):
    planets = {
        "Sun": get_planet_pos("Sun", observer),
        "Moon": get_planet_pos("Moon", observer),
        "Asc": get_planet_pos("Asc", observer),
        "MC": get_planet_pos("MC", observer),
        "DS": get_planet_pos("DS", observer),
        "IC": get_planet_pos("IC", observer)
    }

    results = []
    pairs = [("Sun", "Moon"), ("Sun", "Asc"), ("Sun", "MC"), ("Sun", "IC") ,("Sun", "DS"),
             ("Moon", "Asc"), ("Moon", "MC"), ("Moon", "IC"), ("Moon", "DS")]

    for p1, p2 in pairs:
        angle = abs(planets[p1] - planets[p2]) % 360
        for aspect_angle, symbol in ASPECTS.items():
            if abs(angle - aspect_angle) <= ORB:
                results.append(f"{symbol} {p1}-{p2} ({angle:.1f}°)")
    return results

# Устанавливаем время начала торгов NYSE
ny_time = datetime.now(NY_TZ).replace(hour=0, minute=00, second=0)
start_date = NY_TZ.localize(ny_time) if ny_time.tzinfo is None else ny_time

observer = ephem.Observer()
observer.lat, observer.lon = OBSERVER_LAT, OBSERVER_LON

print(f"Анализ аспектов ({start_date.strftime('%Y-%m-%d')}):")
print("Время  | Аспекты")
print("-------|--------")

for minute in range(0, 1440, STEP_MINUTES):  # 6.5 часов с шагом 15 минут
    current_date = start_date + timedelta(minutes=minute)
    observer.date = current_date
    aspects = check_aspects(current_date, observer)
    if aspects:
        print(f"{current_date.strftime('%H:%M')} | {' | '.join(aspects)}")
