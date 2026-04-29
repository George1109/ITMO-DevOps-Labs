import telebot
import requests
import os

# Пока что (в "плохом" варианте) берем токен из переменных окружения
# которые мы пропишем прямо в docker-compose
TOKEN = os.getenv("TELEGRAM_TOKEN")
# URL нашего микросервиса погоды внутри сети Docker
WEATHER_SERVICE_URL = "http://weather-logic:5000/weather"

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Напиши город, и я пришлю детальный прогноз.")


@bot.message_handler(func=lambda message: True)
def get_weather(message):
    city = message.text
    try:
        # Отправляем запрос в наш микросервис
        response = requests.get(f"{WEATHER_SERVICE_URL}?address={city}")

        if response.status_code == 200:
            data = response.json()

            # Формируем красивый ответ из JSON
            msg = f"🏙 **Погода в {data['city']}**\n\n"

            first_day = data['daily_forecast'][0]['date']
            msg += f"⏳ **Ближайшие часы ({first_day}):**\n"
            for hour in data['hourly_forecast'][:6]:
                temp = round(float(hour['temp']), 1)
                pop = hour['precip_prob']

                # --- МАГИЯ ОЧИСТКИ ДАТЫ ---
                raw_date = str(hour['date'])
                if " " in raw_date:  # Если дата длинная (с днем недели и т.д.)
                    # Пытаемся вытащить время (оно обычно в формате 13:00:00)
                    # Если формат Tue, 28 Apr 2026 13:00:00 GMT, то время под индексом 4
                    parts = raw_date.split()
                    for part in parts:
                        if ":" in part:
                            display_time = ":".join(part.split(":")[:2])  # Оставляем HH:MM
                            break
                    else:
                        display_time = raw_date  # Если не нашли : , оставляем как есть
                else:
                    display_time = raw_date

                msg += f"`{display_time}`: `{temp}°C` | 💧 `{pop}%`\n"

            msg += "📅 **Прогноз на неделю:**\n"
            for day in data['daily_forecast']:
                t_min = round(float(day['temp_min']), 1)
                t_max = round(float(day['temp_max']), 1)
                msg += f"• {day['date']}: `{t_min}°C` ... `{t_max}°C`\n"

            bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Город не найден или сервис недоступен.")

    except Exception as e:
        bot.send_message(message.chat.id, f"🔥 Ошибка связи с сервисом погоды: {e}")


bot.infinity_polling()