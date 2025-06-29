# 🚀 Быстрый запуск

## 1. Подготовка
```bash
# Склонируйте репозиторий
git clone <repository-url>
cd <project-directory>

# Установите зависимости
pip install -r requirements.txt

# Скопируйте пример конфигурации
cp .env.example .env
```

## 2. Настройка .env файла
Отредактируйте `.env` файл с вашими настройками:

### Обязательные параметры:
```env
# Telegram (ОБЯЗАТЕЛЬНО для работы)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Путь к фотографиям (ОБЯЗАТЕЛЬНО)
PHOTO_DIR=/path/to/your/photos

# API для детекции NSFW (опционально)
DETECT_NUDE_API_URL=http://your-nsfw-api.com/detect
```

## 3. Запуск
```bash
# Локальный запуск
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Или через Docker
docker build -t truenas-app .
docker run -p 8000:8000 --env-file .env truenas-app
```

## 4. Проверка работы
Откройте в браузере:
- **API документация**: http://localhost:8000/docs
- **Статус**: http://localhost:8000/health
- **Конфигурация**: http://localhost:8000/config

## 5. Первые тесты

### Проверить статус Telegram
```bash
curl http://localhost:8000/telegram/status
```

### Получить статистику фотографий
```bash
curl http://localhost:8000/photos/stats
```

### Запустить задачу планировщика вручную
```bash
curl -X POST http://localhost:8000/scheduler/jobs/random_time_post/run
```

### Отправить случайное фото
```bash
curl -X POST http://localhost:8000/telegram/post-random \
     -F "caption=Тестовое фото 📸"
```

## 🔧 Возможные проблемы

### Telegram не настроен
```json
{
  "configured": false,
  "bot_token_set": false,
  "chat_id_set": false
}
```
**Решение**: Проверьте настройки `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` в `.env`

### Папка с фото не найдена
```json
{
  "error": "Photo directory not found"
}
```
**Решение**: Убедитесь что `PHOTO_DIR` указывает на существующую папку

### API детекции недоступен
```json
{
  "status": "error",
  "error": "connection_error"
}
```
**Решение**: Проверьте `DETECT_NUDE_API_URL` или отключите автоматическое сканирование

## 📚 Следующие шаги

1. **Изучите API** - откройте http://localhost:8000/docs
2. **Настройте расписание** - отредактируйте переменные `*_SCHEDULE` 
3. **Проверьте логи** - убедитесь что задачи выполняются корректно
4. **Настройте production** - см. [DEVELOPMENT.md](DEVELOPMENT.md)