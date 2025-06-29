# Руководство по разработке

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения
```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл с вашими настройками
nano .env
```

### 3. Запуск приложения
```bash
# Локальный запуск
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Или через Docker
docker build -t truenas-app .
docker run -p 8000:8000 --env-file .env truenas-app
```

## Тестирование

### Запуск тестов
```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# Только unit тесты
pytest -m unit

# С покрытием кода
pip install pytest-cov
pytest --cov=app tests/
```

### Линтинг и форматирование
```bash
# Проверка кода
flake8 app/ tests/

# Автоформатирование
black app/ tests/

# Проверка типов
mypy app/
```

## Структура проекта

```
app/
├── config/          # Конфигурация приложения
├── handlers/        # Обработчики задач
├── scheduler/       # Планировщик
└── main.py         # Главный модуль

tests/              # Тесты
├── test_handlers.py
└── test_config.py

helm/               # Kubernetes деплой
└── truenas-app/

.github/workflows/  # CI/CD
└── ci.yml
```

## API Endpoints

### GET /health
Проверка работоспособности сервиса

### GET /
Основная информация о сервисе

## Переменные окружения

См. файл `.env.example` для полного списка доступных переменных.

### Критически важные:
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `TELEGRAM_CHAT_ID` - ID чата для отправки сообщений
- `DETECT_NUDE_API_URL` - URL API для детекции NSFW контента

## Развертывание

### Docker
```bash
# Сборка
./build.sh <dockerhub_username> <repository_name>

# Или с отключенным кешем
./build.sh <dockerhub_username> <repository_name> false
```

### Kubernetes (Helm)
```bash
cd helm/truenas-app
helm install truenas-app . --values values.yaml
```

## Отладка

### Логи
```bash
# Docker контейнер
docker logs <container_id>

# Kubernetes pod
kubectl logs <pod_name>
```

### Проверка планировщика
Планировщик логирует информацию о запуске задач. Проверьте логи на наличие:
- "Scheduler started in background thread"
- "Добавлена задача X с расписанием Y"

## Известные проблемы

1. **Модуль telegram-post отсутствует** - используется заглушка
2. **Требуется настройка внешнего API** для детекции NSFW
3. **Отсутствует graceful shutdown** планировщика

## Contribution

1. Создайте ветку для вашей функции
2. Напишите тесты
3. Убедитесь что все тесты проходят
4. Создайте Pull Request