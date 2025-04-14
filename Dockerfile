FROM python:3.9-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения и инициализируем подмодули
COPY . .
RUN git submodule update --init --recursive --remote
RUN pip install -e .

# Создаем директорию для данных
RUN mkdir -p /data

# Устанавливаем bash как оболочку по умолчанию
SHELL ["/bin/bash", "-c"]

CMD ["python", "-m", "app.main"] 