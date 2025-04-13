# TrueNAS Scale Application

Это приложение для TrueNAS Scale, разработанное на Python с использованием FastAPI.

## Требования

- Python 3.8+
- TrueNAS Scale
- Зависимости из requirements.txt

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Функциональность

- API для взаимодействия с TrueNAS Scale
- Управление ресурсами системы
- Мониторинг состояния
- Конфигурация системы

## Лицензия

MIT 