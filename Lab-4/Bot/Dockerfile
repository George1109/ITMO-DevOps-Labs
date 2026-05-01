FROM python:3.14-slim
WORKDIR /app

COPY Bot/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./Bot .

CMD ["python", "telegram_bot.py"]
