# 1. Используем легкий образ Python
FROM python:3.13-slim

# 2. Указываем рабочую папку
WORKDIR /app

# 3. Копируем зависимости
COPY weather/requirements.txt .

# 4. Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файл конфигурации
COPY Bot/config.py . 
# Копируем код сервиса погоды
COPY weather/ . 

EXPOSE 5000

# 6. Запускаем именно Flask-сервис
CMD ["python", "weather_service.py"]
