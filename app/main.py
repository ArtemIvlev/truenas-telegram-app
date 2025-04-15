from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import subprocess
import logging
import asyncio
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Nude Detection Service")

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к скрипту detect_nude.py
SCRIPT_PATH = '/app/nude_catalog/detect_nude/detect_nude.py'

async def run_script():
    """Асинхронный запуск скрипта"""
    process = await asyncio.create_subprocess_exec(
        'python3', SCRIPT_PATH,
        cwd='/app/nude_catalog',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Читаем вывод в фоновом режиме
    async def log_output(stream, prefix):
        while True:
            line = await stream.readline()
            if not line:
                break
            logger.info(f"{prefix}: {line.decode().strip()}")
    
    # Запускаем чтение вывода и сохраняем задачи
    stdout_task = asyncio.create_task(log_output(process.stdout, "STDOUT"))
    stderr_task = asyncio.create_task(log_output(process.stderr, "STDERR"))
    
    # Дожидаемся завершения обеих задач
    await asyncio.gather(stdout_task, stderr_task)
    
    return process

@app.post("/run")
async def run_detection():
    try:
        logger.info("Запуск detect_nude.py")
        
        if not os.path.exists(SCRIPT_PATH):
            logger.error(f"Скрипт не найден по пути: {SCRIPT_PATH}")
            return JSONResponse(
                status_code=500,
                content={"error": "Скрипт detect_nude.py не найден"}
            )
        
        # Запускаем скрипт асинхронно
        asyncio.create_task(run_script())
        
        # Сразу возвращаем ответ, что скрипт запущен
        return JSONResponse(content={
            "status": "started",
            "message": "Скрипт detect_nude.py запущен в фоновом режиме"
        })
    
    except Exception as e:
        logger.error(f"Ошибка при запуске detect_nude.py: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    version = os.getenv("APP_VERSION", "development")
    logger.info(f"Starting application version: {version}")

@app.get("/")
async def root():
    return {"message": "Nude Detection Service API"} 