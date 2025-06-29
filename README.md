# TrueNAS Telegram Scheduler API

Полнофункциональная система для автоматического управления фотографиями с планировщиком задач, детекцией NSFW контента и публикацией в Telegram.

## Особенности

- 📅 **Планировщик задач** - автоматическое выполнение по расписанию
- 🔍 **NSFW детекция** - автоматическое обнаружение неподходящего контента
- 📸 **Telegram интеграция** - публикация фотографий в Telegram каналы
- 🚀 **FastAPI** - современное REST API с автодокументацией
- 🐳 **Docker** - готовая контейнеризация
- ☸️ **Kubernetes** - деплой через Helm charts
- 🧪 **Тестирование** - полное покрытие тестами

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка
```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл с вашими настройками
nano .env
```

### 3. Запуск
```bash
# Локальный запуск с автоперезагрузкой
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Или через Docker
docker build -t truenas-app .
docker run -p 8000:8000 --env-file .env truenas-app
```

### 4. Документация API
Откройте в браузере: http://localhost:8000/docs

## API Endpoints

### 🏠 Основные
- `GET /` - Информация о сервисе
- `GET /health` - Проверка работоспособности
- `GET /config` - Текущая конфигурация

### ⏰ Планировщик
- `GET /scheduler/status` - Статус планировщика
- `GET /scheduler/jobs` - Список задач
- `POST /scheduler/jobs/{job_id}/run` - Запуск задачи вручную

### 📱 Telegram
- `POST /telegram/post-random` - Опубликовать случайное фото
- `POST /telegram/post-file` - Отправить конкретный файл
- `GET /telegram/status` - Статус подключения

### 📸 Фотографии
- `GET /photos/stats` - Статистика фотографий
- `GET /photos/random-list` - Список случайных фото

### 🔞 NSFW детекция
- `POST /nsfw/scan-all` - Сканировать все фотографии
- `POST /nsfw/scan-single` - Проверить одно изображение
- `GET /nsfw/review-stats` - Статистика проверенных файлов
- `GET /nsfw/settings` - Настройки детектора

## Примеры использования

### Отправка случайной фотографии
```bash
curl -X POST "http://localhost:8000/telegram/post-random" \
     -F "caption=Красивое фото дня! 📸"
```

### Проверка изображения на NSFW
```bash
curl -X POST "http://localhost:8000/nsfw/scan-single" \
     -F "file=@photo.jpg"
```

### Запуск полного сканирования
```bash
curl -X POST "http://localhost:8000/nsfw/scan-all"
```

### Ручной запуск задачи планировщика
```bash
curl -X POST "http://localhost:8000/scheduler/jobs/detect_nude/run"
```

## Конфигурация

См. файл `.env.example` для полного списка настроек.

### Критически важные переменные:
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `TELEGRAM_CHAT_ID` - ID чата для публикации
- `DETECT_NUDE_API_URL` - URL API для NSFW детекции
- `PHOTO_DIR` - путь к директории с фотографиями

## Развертывание

### Docker
```bash
./build.sh <dockerhub_username> <repository_name>
```

### Kubernetes
```bash
cd helm/truenas-app
helm install truenas-app . --values values.yaml
```

## Разработка

См. [DEVELOPMENT.md](DEVELOPMENT.md) для подробной информации по разработке.

## Лицензия

MIT 