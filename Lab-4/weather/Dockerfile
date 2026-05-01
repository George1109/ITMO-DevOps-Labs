# 1. Используем тот же легкий образ Python
FROM python:3.10-slim

# 2. Указываем рабочую папку
WORKDIR /app

# 3. Копируем зависимости
# В этом сервисе они тяжелее (Pandas весит прилично), 
# поэтому кеширование здесь особенно важно.
COPY weather/requirements.txt .

# 4. Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файл конфигурации из папки Bot (или корня, если он там)
COPY Bot/config.py . 
# Копируем код сервиса погоды
COPY weather/ . 

# 6. Подсказываем Docker, что наш сервис работает на 5000 порту
EXPOSE 5000

# 7. Запускаем именно Flask-сервис
CMD ["python", "weather_service.py"]