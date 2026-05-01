import telebot
import requests
import os
from telebot import types
# ИМПОРТИРУЕМ НАШ КОНФИГ
from config import config

# ВАЖНО: берем токен из словаря, который вернул Vault
# Ключ 'telegram_id' мы видели в твоем успешном тесте
TOKEN = config.get("telegram_id")
WEATHER_SERVICE_URL = os.getenv("WEATHER_SERVICE_URL", "http://weather-logic:5000/weather")

if not TOKEN:
    print("❌ Ошибка: Telegram Token не найден в Vault!")
    exit(1)

bot = telebot.TeleBot(TOKEN)


# Функция для создания Inline-кнопок (они крепятся к сообщению)
def get_inline_menu(city):
    markup = types.InlineKeyboardMarkup()
    # В callback_data зашиваем и тип прогноза, и название города через ":"
    # Это позволит боту узнать город, когда кнопка будет нажата
    btn_hourly = types.InlineKeyboardButton("⏳ Почасовой", callback_data=f"wh:{city}")
    btn_daily = types.InlineKeyboardButton("📅 На неделю", callback_data=f"wd:{city}")
    markup.add(btn_hourly, btn_daily)
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_instructions(message):
    instruction = (
        "🤖 **Бот-синоптик**\n\n"
        "Чтобы узнать погоду, просто **напиши название города**.\n\n"
        "📖 **Инструкция:**\n"
        "Рекомендуемый формат входных данных\n"
        "• Дом\n"
        "• Улица\n"
        "• Город\n"
        "• Область\n"
        "• Страна\n"
        "• Почтовый индекс\n"
        "Все параметры являются необязательными, вам следует использовать только те,"
        " которые относятся к адресу, который вы хотите запросить"
    )
    # Обычная кнопка только для вызова инструкции
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📖 Инструкция"))

    bot.send_message(message.chat.id, instruction, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "📖 Инструкция")
def instruction_button(message):
    send_instructions(message)


@bot.message_handler(func=lambda message: True)
def handle_city_input(message):
    if message.text.startswith('/'):
        return

    city = message.text
    # Просто спрашиваем, какой прогноз нужен для этого города
    bot.send_message(
        message.chat.id,
        f"📍 Город: **{city.upper()}**\nВыберите тип прогноза:",
        parse_mode="Markdown",
        reply_markup=get_inline_menu(city)
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Разбираем callback_data (например, "wh:Moscow")
    forecast_type, city = call.data.split(':')

    try:
        response = requests.get(f"{WEATHER_SERVICE_URL}?address={city}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            msg = ""

            if forecast_type == "wh":  # Почасовой
                msg = f"🏙 **{data['city']} (Почасовой)**\n"
                msg += "───────────────────\n"
                for hour in data['hourly_forecast'][:8]:
                    temp = round(float(hour['temp']), 1)
                    icon = "🌡" if temp > 0 else "❄️"
                    msg += f"🕒 `{hour['display_time']}`  {icon} `{temp}°C`  💧 `{hour['precip_prob']}%`\n"

            elif forecast_type == "wd":  # Недельный
                msg = f"🏙 **{data['city']} (На неделю)**\n"
                msg += "───────────────────\n"
                for day in data['daily_forecast']:
                    t_min = round(float(day['temp_min']), 1)
                    t_max = round(float(day['temp_max']), 1)
                    msg += f"• {day['date']}: `{t_min}°C` ... `{t_max}°C`\n"

            # Редактируем текущее сообщение, добавляя результат и оставляя кнопки для переключения
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=msg,
                parse_mode="Markdown",
                reply_markup=get_inline_menu(city)
            )
        else:
            bot.answer_callback_query(call.id, "❌ Город не найден")

    except Exception:
        bot.answer_callback_query(call.id, "🔥 Ошибка сервиса")


bot.infinity_polling()
