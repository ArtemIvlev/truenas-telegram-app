import os
import subprocess
from app.handlers.base_handler import BaseHandler
from app.scheduler.scheduler import logger

class DetectNudeHandler(BaseHandler):
    def __init__(self):
        self.nude_catalog_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'nude_catalog')
        
    def handle(self):
        try:
            logger.info("Запуск detect_nude.py")
            script_path = os.path.join(self.nude_catalog_path, 'detect_nude', 'detect_nude.py')
            
            if not os.path.exists(script_path):
                logger.error(f"Скрипт не найден по пути: {script_path}")
                return
                
            result = subprocess.run(['python3', script_path], 
                                 cwd=self.nude_catalog_path,
                                 capture_output=True,
                                 text=True)
            
            if result.returncode == 0:
                logger.info("detect_nude.py успешно выполнен")
                if result.stdout:
                    logger.info(f"Вывод скрипта: {result.stdout}")
            else:
                logger.error(f"Ошибка при выполнении detect_nude.py: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Ошибка при запуске detect_nude.py: {str(e)}") 