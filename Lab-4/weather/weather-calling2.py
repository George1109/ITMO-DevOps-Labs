import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import requests
from urllib.parse import quote
# --- Работа geoapi ---
# api сайта
url = "https://nominatim.openstreetmap.org/search?"

print("Введите адрес")

address = input()

#Вводим параметры(q - адрес, который мы ищем, формат - формат выдаваемого сайта
#лимит - сколько ответов получим
params = {
    "q":address,
    "format":"json",
    "limit":1
}

#заголовки = необходимые для этого сайта
#юзер агент - тот кто использует
headers = {
    "User-Agent":"app"
}
#получаем респонс
response = requests.get(url, params=params, headers=headers)

data = response.json()

lat = data[0]["lat"]
lon = data[0]["lon"]


# --- Работа weather api ---
# --- НАСТРОЙКА КЛИЕНТА И СЕТИ ---
# Создаем кэш, чтобы не запрашивать данные чаще одного раза в час (экономим трафик и время)
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
# Настраиваем автоматические попытки переподключения, если сервер не ответил сразу
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# --- НАСТРОЙКИ ОТОБРАЖЕНИЯ PANDAS ---
# Заставляем pandas показывать все колонки без сокращений (вместо точек "...")
pd.set_option('display.max_columns', None)
# Расширяем область вывода в терминале, чтобы таблица не переносилась на новую строку
pd.set_option('display.width', 1000)

# --- ЗАПРОС ДАННЫХ ---
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
    "hourly": ["temperature_2m", "precipitation", "precipitation_probability"],
    "timezone": "Europe/Moscow", # Указываем пояс, чтобы API само рассчитало смещение времени
}
responses = openmeteo.weather_api(url, params = params)
response = responses[0] # Работаем с первым объектом из списка ответов

# --- ВЫВОД ОБЩЕЙ ИНФОРМАЦИИ ---
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# --- ОБРАБОТКА ПОЧАСОВОГО ПРОГНОЗА (HOURLY) ---
hourly = response.Hourly()
# Извлекаем данные переменных в виде массивов (температура, осадки, вероятность осадков)
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()

# Создаем временную шкалу для каждого часа, учитывая локальное смещение времени
hourly_data = {"date": pd.date_range(
    start = pd.to_datetime(hourly.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
    end =  pd.to_datetime(hourly.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
    freq = pd.Timedelta(seconds = hourly.Interval()),
    inclusive = "left"
)}

# Наполняем словарь почасовыми данными
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation"] = hourly_precipitation
hourly_data["precipitation_probability"] = hourly_precipitation_probability

# Создаем DataFrame и форматируем дату для вывода (убираем лишние секунды и пояса)
hourly_dataframe = pd.DataFrame(data = hourly_data)
hourly_dataframe['date'] = hourly_dataframe['date'].dt.strftime('%Y-%m-%d %H:%M')

# Выводим первые 24 часа прогноза
print("\nHourly data (First 24 hours)\n", hourly_dataframe.head(24))

# --- ОБРАБОТКА ЕЖЕДНЕВНОГО ПРОГНОЗА (DAILY) ---
daily = response.Daily()
# Извлекаем температурные экстремумы
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
# Время восхода и заката берем как целые числа (Unix Timestamp)
daily_sunrise = daily.Variables(2).ValuesInt64AsNumpy()
daily_sunset = daily.Variables(3).ValuesInt64AsNumpy()

# Формируем список дней (дат) со смещением по часовому поясу
daily_data = {"date": pd.date_range(
    start = pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit = "s", utc = True),
    end =  pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit = "s", utc = True),
    freq = pd.Timedelta(seconds = daily.Interval()),
    inclusive = "left"
)}

# Добавляем температуры и конвертируем восход/закат в объекты времени с учетом часового пояса
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["sunrise"] = pd.to_datetime(daily_sunrise + response.UtcOffsetSeconds(), unit = "s", utc = True)
daily_data["sunset"] = pd.to_datetime(daily_sunset + response.UtcOffsetSeconds(), unit = "s", utc = True)

# Создаем итоговый DataFrame для ежедневных данных
daily_dataframe = pd.DataFrame(data = daily_data)

# Финальное форматирование: оставляем только даты в 'date' и только время в 'sunrise/sunset'
daily_dataframe['date'] = daily_dataframe['date'].dt.strftime('%Y-%m-%d')
daily_dataframe['sunrise'] = daily_dataframe['sunrise'].dt.strftime('%H:%M')
daily_dataframe['sunset'] = daily_dataframe['sunset'].dt.strftime('%H:%M')

# Выводим готовую ежедневную таблицу
print("\nDaily data\n", daily_dataframe)