FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
COPY app/ app/
COPY nude_catalog/ nude_catalog/

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя без прав root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 