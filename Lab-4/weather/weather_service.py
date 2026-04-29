from flask import Flask, request, jsonify
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import requests
import datetime

app = Flask(__name__)

# --- Глобальная настройка клиента (делаем один раз при запуске сервера) ---
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def get_weather_data(address):
    # 1. Геокодинг (Адрес -> Координаты)
    geo_url = "https://nominatim.openstreetmap.org/search?"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "WeatherBotApp/1.0"}

    res = requests.get(geo_url, params=params, headers=headers)
    geo_data = res.json()
    if not geo_data:
        return None

    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

    # 2. Запрос к Open-Meteo
    url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "hourly": ["temperature_2m", "precipitation", "precipitation_probability"],
        "timezone": "auto",
    }

    responses = openmeteo.weather_api(url, params=weather_params)
    response = responses[0]

    utc_offset = response.UtcOffsetSeconds()
    local_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=utc_offset)

    # 3. Обработка почасовых данных (на 24 часа)
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time() + utc_offset, unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd() + utc_offset, unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temp": hourly.Variables(0).ValuesAsNumpy(),
        "precip_prob": hourly.Variables(2).ValuesAsNumpy()
    }

    hourly_df = pd.DataFrame(data=hourly_data)

    # --- ВОТ ТУТ МАГИЯ ФИЛЬТРАЦИИ ---
    # Отрезаем всё, что было раньше текущего локального времени города
    # (с небольшим запасом в минус 15 минут, чтобы текущий час тоже попал)
    actual_forecast = hourly_df[hourly_df['date'] >= (local_now - datetime.timedelta(minutes=15))]

    # Берем ближайшие 8 часов
    hourly_slice = actual_forecast.head(8).copy()
    hourly_slice['display_time'] = hourly_slice['date'].dt.strftime('%H:%M')


    # 4. Обработка ежедневных данных (на неделю)
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "temp_max": daily.Variables(0).ValuesAsNumpy(),
        "temp_min": daily.Variables(1).ValuesAsNumpy()
    }
    daily_df = pd.DataFrame(data=daily_data)
    daily_df['date'] = daily_df['date'].dt.strftime('%d.%m')  # Формат: День.Месяц

    # --- САМОЕ ВАЖНОЕ: Превращаем таблицы в JSON-структуру ---
    return {
        "city": address,
        "hourly_forecast": hourly_slice.to_dict(orient='records'),
    "daily_forecast": daily_df.to_dict(orient='records')
    }


@app.route('/weather', methods=['GET'])
def weather_api():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "No address"}), 400

    data = get_weather_data(address)
    if not data:
        return jsonify({"error": "Location not found"}), 404

    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)