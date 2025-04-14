# Nude Detection Service

Веб-сервис для определения NSFW контента на изображениях.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Настройка

1. Создайте файл `.env` на основе `.env.example`
2. Укажите путь к модели в переменной `MODEL_PATH`

## Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /detect
Загрузка и анализ изображения

Пример запроса:
```bash
curl -X POST "http://localhost:8000/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@image.jpg"
```

Пример ответа:
```json
{
    "filename": "image.jpg",
    "is_nude": false,
    "confidence": 0.12
}
```

### GET /health
Проверка работоспособности сервиса

## Лицензия

MIT 