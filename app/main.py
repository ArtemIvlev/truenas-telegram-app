from app.handlers.detect_nude_handler import DetectNudeHandler
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.scheduler.scheduler import Scheduler
from app.handlers.random_time_handler import RandomTimeHandler
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="scheduler")

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    version = os.getenv("APP_VERSION", "development")
    logger.info(f"Starting application version: {version}")
    
    # Инициализируем обработчики
    random_time_handler = RandomTimeHandler()
    detect_nude_handler = DetectNudeHandler()
    
    # Добавляем задачи в шедулер
    scheduler.add_job(
        "random_time_post",
        random_time_handler.handle,
        os.getenv("RANDOM_TIME_SCHEDULE", "0 8 * * *"),
        run_now=False
    )

    scheduler.add_job(
        "detect_nude",
        detect_nude_handler.handle,
        os.getenv("DETECT_NUDE_SCHEDULE", "0 3 * * *"),
        run_now=False
    )

    # Запускаем шедулер в отдельном потоке
    scheduler_thread = threading.Thread(target=scheduler.run_forever, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler started in background thread")

@app.get("/")
async def root():
    return {"message": "scheduler API"} 