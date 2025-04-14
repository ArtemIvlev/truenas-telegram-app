# Этап сборки зависимостей
FROM python:3.9-slim as builder

# Установка системных зависимостей только для сборки
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Создание и активация виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование только файлов зависимостей для лучшего кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Этап сборки кода
FROM builder as code

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY app/ app/
COPY nude_catalog/ nude_catalog/

# Финальный этап
FROM python:3.9-slim

# Копирование только необходимых системных библиотек
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копирование виртуального окружения из этапа сборки
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование кода из этапа сборки кода
COPY --from=code /app /app

# Создание пользователя и настройка прав
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Команда по умолчанию
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 