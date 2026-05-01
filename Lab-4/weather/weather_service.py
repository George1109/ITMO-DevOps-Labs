from flask import Flask, request, jsonify
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import requests
import datetime
from config import config

# Создаём экземпляр веб приложения
app = Flask(__name__)

# Берём секреты из хранилища
WEATHER_KEY = config.get('weather_api')
GEO_KEY = config.get('geo_api')
# Глобальная настройка клиента
# 1. Когда обновлять кэш
# 2. Сколько попыток на подключение/ какое время прибавлять к ожиданию подключения 0,2 -> 0,4 ...
# 3. Создаём клиента, подключённого к обновлённому кэшу
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


# Функция подключения погоды
def get_weather_data(address):
    # Запрос идет к юрл:
    geo_url = GEO_KEY
    # "q": address - поисковой запрос/формат/лимит
    params = {"q": address, "format": "json", "limit": 1}
    # Указываем кто отправляет запрос
    headers = {"User-Agent": "WeatherBotApp/1.0"}

    # Выполняется гет запрос по параметрам
    res = requests.get(geo_url, params=params, headers=headers)
    # Формат ответа сохраняется в переменную
    geo_data = res.json()
    # Обработка ошибки
    if not geo_data:
        return None
    # Получаем координаты
    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

    # Запрос к Open-Meteo
    url = WEATHER_KEY
    # Уже параметры погодного сайта
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "hourly": ["temperature_2m", "precipitation", "precipitation_probability"],
        "timezone": "auto",
    }

    # Делаем запрос к опенметео
    # Берём только нулевой элемент
    # Нам нужен только город
    responses = openmeteo.weather_api(url, params=weather_params)
    response = responses[0]

    # Получаем часовой пояс для выбранного города
    # Получаем локальное время
    utc_offset = response.UtcOffsetSeconds()
    local_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=utc_offset)

    # Обработка почасовых данных
    # Получаем объект с почасовыми данными
    hourly = response.Hourly()
    # Создаём словарь дата фрейм
    hourly_data = {
        # Создаём временную шкалу с началом, концом и промежутками
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time() + utc_offset, unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd() + utc_offset, unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        # Берём первый элемент (температура)
        "temp": hourly.Variables(0).ValuesAsNumpy(),
        # Берём 3 элемент ожидание осадков
        "precip_prob": hourly.Variables(2).ValuesAsNumpy()
    }

    # Создаём пандас датафрейм
    hourly_df = pd.DataFrame(data=hourly_data)

    # Фильтрация с запасом в 15 минут
    actual_forecast = hourly_df[hourly_df['date'] >= (local_now - datetime.timedelta(minutes=15))]

    # Берем ближайшие 8 часов
    hourly_slice = actual_forecast.head(8).copy()
    hourly_slice['display_time'] = hourly_slice['date'].dt.strftime('%H:%M')

    # Обработка ежедневных данных (на неделю)
    # То же что и в почасовом
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        # Берём максимальную и минимальную температуру
        "temp_max": daily.Variables(0).ValuesAsNumpy(),
        "temp_min": daily.Variables(1).ValuesAsNumpy()
    }
    # Создаем дата фрейм
    daily_df = pd.DataFrame(data=daily_data)
    # Форматируем
    daily_df['date'] = daily_df['date'].dt.strftime('%d.%m')

    # Возвращаем почасовой и недельный фреймы под новыми именами
    return {
        "city": address,
        "hourly_forecast": hourly_slice.to_dict(orient='records'),
        "daily_forecast": daily_df.to_dict(orient='records')
    }


# Декоратор Фласк — регистрирует функцию /weather для гет запроса
@app.route('/weather', methods=['GET'])
def weather_api():
    # Пытаемся получить адрес
    address = request.args.get('address')
    # Обработка этого запроса
    if not address:
        return jsonify({"error": "No address"}), 400

    # Получаем данные по адресу
    data = get_weather_data(address)
    if not data:
        return jsonify({"error": "Location not found"}), 404

    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
