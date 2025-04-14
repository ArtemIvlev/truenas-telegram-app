from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import subprocess
import logging
import asyncio
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(title="Nude Detection Service")

# Путь к скрипту detect_nude.py
NUDE_CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nude_catalog')
SCRIPT_PATH = os.path.join(NUDE_CATALOG_PATH, 'detect_nude', 'detect_nude.py')

async def run_script():
    """Асинхронный запуск скрипта"""
    process = await asyncio.create_subprocess_exec(
        'python3', SCRIPT_PATH,
        cwd=NUDE_CATALOG_PATH,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
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
        process = await run_script()
        
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