FROM python:3.13.5-slim

ARG APP_PATH=.

# Установка curl (если он действительно нужен; можно убрать, если не используется)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем pyproject.toml для установки зависимостей
COPY ${APP_PATH}/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ${APP_PATH} /app

CMD ["python", "main.py"]