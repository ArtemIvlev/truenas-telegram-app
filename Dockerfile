FROM python:3.9-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .
RUN pip install -e .

# Создаем директорию для данных
RUN mkdir -p /data

# Запускаем приложение
CMD ["python", "-m", "app.main"] 