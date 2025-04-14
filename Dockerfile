# Этап сборки
FROM python:3.9-slim as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание и активация виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY nude_catalog /app/nude_catalog
COPY app/main.py /app/
COPY setup.py /app/

# Установка пакета nude_catalog в режиме разработки
WORKDIR /app
RUN pip install -e .

# Этап финального образа
FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из этапа сборки
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Копирование приложения
COPY --from=builder /app /app

# Создание пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Установка переменных окружения
ENV PHOTO_DIR="/mnt/smb/OneDrive/Pictures/!Фотосессии/" \
    DB_FILE="/app/nude_catalog/DB/photos.db" \
    REVIEW_DIR="review" \
    TELEGRAM_DB="/app/nude_catalog/telegram_bot/telegram_bot.db" \
    TABLE_NAME="photos_ok" \
    NSFW_THRESHOLD=0.8 \
    CLIP_THRESHOLD=0.8 \
    MIN_IMAGE_SIZE=2500 \
    MAX_IMAGE_SIZE=10000

# Переключение на пользователя
USER appuser

# Рабочая директория
WORKDIR /app

# Добавляем ARG для версии
ARG VERSION=latest
ENV APP_VERSION=${VERSION}

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD echo "Starting application version: ${APP_VERSION}" && uvicorn main:app --host 0.0.0.0 --port 8000 