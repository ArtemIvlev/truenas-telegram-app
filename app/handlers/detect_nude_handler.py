import os
import requests
from app.handlers.base_handler import BaseHandler
from app.scheduler.scheduler import logger

class DetectNudeHandler(BaseHandler):
    def __init__(self):
        self.api_url = "http://192.168.2.228:8888/run"
        
    def handle(self):
        try:
            logger.info("Отправка запроса на detect_nude сервис")
            
            response = requests.post(self.api_url)
            
            if response.status_code == 200:
                logger.info("detect_nude сервис успешно выполнен")
                if response.text:
                    logger.info(f"Ответ сервиса: {response.text}")
            else:
                logger.error(f"Ошибка при выполнении detect_nude сервиса: {response.text}")
                
        except Exception as e:
            logger.error(f"Ошибка при отправке запроса к detect_nude сервису: {str(e)}") 