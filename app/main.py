from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import threading
import os
from typing import Dict, List, Optional
from pathlib import Path

from app.config.settings import settings
from app.scheduler.scheduler import Scheduler
from app.handlers.detect_nude_handler import DetectNudeHandler
from app.handlers.random_time_handler import RandomTimeHandler
from app.telegram.post import get_telegram_poster, post_random_photo
from app.nsfw.detector import get_nsfw_detector

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="TrueNAS Telegram Scheduler API",
    description="API для управления планировщиком задач и публикации фотографий в Telegram",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Создаем экземпляр шедулера
scheduler = Scheduler()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные переменные для обработчиков
random_time_handler = None
detect_nude_handler = None

@app.on_event("startup")
async def startup_event():
    """Инициализация приложения при запуске"""
    global random_time_handler, detect_nude_handler
    
    logger.info(f"Starting TrueNAS Telegram Scheduler API version: {settings.APP_VERSION}")
    
    # Проверяем критически важные настройки
    try:
        settings.validate()
        logger.info("Конфигурация прошла валидацию")
    except ValueError as e:
        logger.warning(f"Проблемы с конфигурацией: {e}")
    
    # Инициализируем обработчики
    random_time_handler = RandomTimeHandler()
    detect_nude_handler = DetectNudeHandler()
    
    # Добавляем задачи в шедулер  
    def async_wrapper(async_func):
        """Обертка для выполнения асинхронных функций в синхронном планировщике"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(async_func())
    
    scheduler.add_job(
        "random_time_post",
        random_time_handler.handle,
        settings.RANDOM_TIME_SCHEDULE,
        run_now=False
    )

    def run_detect_nude():
        if detect_nude_handler:
            return async_wrapper(detect_nude_handler.handle)
        else:
            logger.error("detect_nude_handler не инициализирован")
            return {'status': 'error', 'error': 'handler_not_initialized'}
    
    scheduler.add_job(
        "detect_nude",
        run_detect_nude,
        settings.DETECT_NUDE_SCHEDULE,
        run_now=False
    )

    # Запускаем шедулер в отдельном потоке
    scheduler_thread = threading.Thread(target=scheduler.run_forever, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler started in background thread")

# === ОСНОВНЫЕ ЭНДПОИНТЫ ===

@app.get("/", tags=["Main"])
async def root():
    """Основная информация о сервисе"""
    return {
        "service": "TrueNAS Telegram Scheduler API",
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "scheduler": "/scheduler/*",
            "telegram": "/telegram/*",
            "photos": "/photos/*",
            "nsfw": "/nsfw/*",
            "config": "/config"
        }
    }

@app.get("/health", tags=["Main"])
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "scheduler_jobs": len(scheduler.jobs),
        "telegram_configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
    }

# === УПРАВЛЕНИЕ ПЛАНИРОВЩИКОМ ===

@app.get("/scheduler/status", tags=["Scheduler"])
async def get_scheduler_status():
    """Получить статус планировщика"""
    jobs_status = []
    for job_id in scheduler.jobs:
        status = scheduler.get_job_status(job_id)
        jobs_status.append(status)
    
    return {
        "scheduler_running": True,
        "total_jobs": len(scheduler.jobs),
        "jobs": jobs_status
    }

@app.get("/scheduler/jobs", tags=["Scheduler"])
async def list_jobs():
    """Список всех задач планировщика"""
    return {
        "jobs": list(scheduler.jobs.keys()),
        "details": {job_id: scheduler.get_job_status(job_id) for job_id in scheduler.jobs}
    }

@app.post("/scheduler/jobs/{job_id}/run", tags=["Scheduler"])
async def run_job_manually(job_id: str, background_tasks: BackgroundTasks):
    """Запустить задачу вручную"""
    if job_id not in scheduler.jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    handler = scheduler.handlers.get(job_id)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Handler for job {job_id} not found")
    
    # Запускаем задачу в фоне
    background_tasks.add_task(handler)
    
    return {
        "message": f"Job {job_id} started manually",
        "job_id": job_id,
        "status": "running"
    }

# === РАБОТА С TELEGRAM ===

@app.post("/telegram/post-random", tags=["Telegram"])
async def post_random_photo_endpoint(
    caption: Optional[str] = Form(None, description="Подпись к фотографии")
):
    """Опубликовать случайную фотографию в Telegram"""
    try:
        result = await post_random_photo(caption)
        
        if result.get('status') == 'success':
            return {
                "success": True,
                "message": "Фото успешно опубликовано",
                "details": result
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Ошибка публикации: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Ошибка в /telegram/post-random: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telegram/post-file", tags=["Telegram"])
async def post_file_to_telegram(
    file: UploadFile = File(..., description="Файл изображения для отправки"),
    caption: Optional[str] = Form(None, description="Подпись к фотографии")
):
    """Отправить конкретный файл в Telegram"""
    try:
        # Проверяем тип файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")
        
        # Сохраняем временно файл
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / file.filename
        
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Отправляем через Telegram
        poster = await get_telegram_poster()
        result = await poster.post_photo(temp_file_path, caption)
        
        # Удаляем временный файл
        temp_file_path.unlink(missing_ok=True)
        
        if result.get('status') == 'success':
            return {
                "success": True,
                "message": "Файл успешно отправлен",
                "details": result
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка отправки: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в /telegram/post-file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telegram/status", tags=["Telegram"])
async def get_telegram_status():
    """Получить статус подключения к Telegram"""
    return {
        "configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID),
        "bot_token_set": bool(settings.TELEGRAM_BOT_TOKEN),
        "chat_id_set": bool(settings.TELEGRAM_CHAT_ID),
        "api_credentials_set": bool(settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH)
    }

# === РАБОТА С ФОТОГРАФИЯМИ ===

@app.get("/photos/stats", tags=["Photos"])
async def get_photos_stats():
    """Получить статистику по фотографиям"""
    try:
        photo_dir = Path(settings.PHOTO_DIR)
        
        if not photo_dir.exists():
            return {
                "error": "Photo directory not found",
                "directory": str(photo_dir)
            }
        
        # Подсчитываем фотографии
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        photo_count = 0
        total_size = 0
        
        for ext in image_extensions:
            files = list(photo_dir.rglob(f'*{ext}'))
            files.extend(photo_dir.rglob(f'*{ext.upper()}'))
            photo_count += len(files)
            total_size += sum(f.stat().st_size for f in files if f.exists())
        
        return {
            "directory": str(photo_dir),
            "total_photos": photo_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "supported_formats": list(image_extensions)
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /photos/stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/photos/random-list", tags=["Photos"])
async def get_random_photos_list(count: int = 5):
    """Получить список случайных фотографий"""
    try:
        if count > 20:
            raise HTTPException(status_code=400, detail="Максимум 20 фотографий за раз")
        
        poster = await get_telegram_poster()
        photos = await poster.get_random_photos(count)
        
        return {
            "count": len(photos),
            "photos": [{"name": p.name, "path": str(p), "size": p.stat().st_size} for p in photos]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в /photos/random-list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === КОНФИГУРАЦИЯ ===

@app.get("/config", tags=["Config"])
async def get_config():
    """Получить текущую конфигурацию (без секретов)"""
    return {
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL,
        "photo_dir": settings.PHOTO_DIR,
        "schedules": {
            "detect_nude": settings.DETECT_NUDE_SCHEDULE,
            "random_time": settings.RANDOM_TIME_SCHEDULE,
        },
        "thresholds": {
            "nsfw": settings.NSFW_THRESHOLD,
            "clip": settings.CLIP_THRESHOLD,
            "min_image_size": settings.MIN_IMAGE_SIZE,
            "max_image_size": settings.MAX_IMAGE_SIZE,
        },
        "telegram_configured": bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
    }

# === NSFW ДЕТЕКЦИЯ ===

@app.post("/nsfw/scan-all", tags=["NSFW"])
async def scan_all_photos():
    """Запустить полное сканирование всех фотографий на NSFW контент"""
    try:
        detector = get_nsfw_detector()
        result = await detector.process_all_images()
        
        return {
            "success": True,
            "message": "Сканирование завершено",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /nsfw/scan-all: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nsfw/scan-single", tags=["NSFW"])
async def scan_single_photo(
    file: UploadFile = File(..., description="Изображение для проверки на NSFW")
):
    """Проверить одно изображение на NSFW контент"""
    try:
        # Проверяем тип файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")
        
        # Сохраняем временно файл
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / file.filename
        
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        # Проверяем через детектор
        detector = get_nsfw_detector()
        result = await detector.detect_single_image(temp_file_path)
        
        # Удаляем временный файл
        temp_file_path.unlink(missing_ok=True)
        
        return {
            "success": True,
            "message": "Анализ завершен",
            "details": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в /nsfw/scan-single: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nsfw/review-stats", tags=["NSFW"])
async def get_review_stats():
    """Получить статистику папки review (подозрительные изображения)"""
    try:
        detector = get_nsfw_detector()
        stats = detector.get_review_stats()
        
        return {
            "success": True,
            "message": "Статистика получена",
            "details": stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка в /nsfw/review-stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nsfw/settings", tags=["NSFW"])
async def get_nsfw_settings():
    """Получить настройки NSFW детектора"""
    return {
        "api_url": settings.DETECT_NUDE_API_URL,
        "threshold": settings.NSFW_THRESHOLD,
        "min_image_size": settings.MIN_IMAGE_SIZE,
        "max_image_size": settings.MAX_IMAGE_SIZE,
        "photo_dir": settings.PHOTO_DIR,
        "review_dir": settings.REVIEW_DIR
    } 