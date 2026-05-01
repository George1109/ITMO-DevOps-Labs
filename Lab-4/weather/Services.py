import pandas as pd
import requests
import datetime


class WeatherService:
    def __init__(self, openmeteo_client):
        # Передаем готовый клиент openmeteo при создании класса
        self.openmeteo = openmeteo_client
        self.geo_url = "https://nominatim.openstreetmap.org/search?"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"

    def get_coordinates(self, address):
        # Преобразуем адрес в координаты
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "WeatherBotApp/1.0"}

        res = requests.get(self.geo_url, params=params, headers=headers)
        geo_data = res.json()

        if not geo_data:
            return None
        return float(geo_data[0]["lat"]), float(geo_data[0]["lon"])

    def fetch_raw_weather(self, lat, lon):
        # Зона 2: Запрос к Open-Meteo (API Fetching)
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
            "hourly": ["temperature_2m", "precipitation", "precipitation_probability"],
            "timezone": "auto",
        }
        responses = self.openmeteo.weather_api(self.weather_url, params=params)
        return responses[0]

    def process_forecast(self, response, address):
        # Зона 3: Мозг (Pandas & Formatting)
        utc_offset = response.UtcOffsetSeconds()
        local_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=utc_offset)

        # Обработка Почасовых (твой код с pandas)
        hourly = response.Hourly()
        hourly_df = pd.DataFrame({
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time() + utc_offset, unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd() + utc_offset, unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temp": hourly.Variables(0).ValuesAsNumpy(),
            "precip_prob": hourly.Variables(1).ValuesAsNumpy()
        })

        # Фильтруем и готовим к отправке
        actual = hourly_df[hourly_df['date'] >= (local_now - datetime.timedelta(minutes=15))].head(8).copy()
        actual['date'] = actual['date'].dt.strftime('%H:%M')

        # Аналогично для Daily... (пропустил для краткости, логика та же)

        return {
            "city": address,
            "hourly_forecast": actual.to_dict(orient='records')
        }
