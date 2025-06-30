import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from app.handlers.base_handler import BaseHandler
from app.config.settings import settings
from app.scheduler.scheduler import logger
import time

class DetectNudeHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.api_url = settings.DETECT_NUDE_API_URL
        self.schedule_time = settings.DETECT_NUDE_SCHEDULE
        
    def handle(self):
        """Простая отправка запроса на внешний сервис детекции (если настроен)"""
        self.before_run()
        
        # Если API не настроен - просто логируем и завершаем
        if not self.api_url or self.api_url in ['http://localhost:8888/run', 'http://192.168.2.228:8888/run']:
            logger.info("API детекции NSFW не настроен, задача пропущена")
            result = {
                'status': 'skipped', 
                'message': 'NSFW API not configured',
                'note': 'Настройте DETECT_NUDE_API_URL для включения функции'
            }
            self.after_run(result)
            return result
        
        try:
            logger.info(f"Отправка запроса на сервис детекции: {self.api_url}")
            
            response = requests.post(
                self.api_url,
                timeout=settings.REQUEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = {
                    'status': 'success',
                    'response': response.text[:200] if response.text else 'OK'  # Ограничиваем длину
                }
                logger.info("Сервис детекции NSFW выполнен успешно")
                self.after_run(result)
                return result
            else:
                result = {
                    'status': 'api_error',
                    'error': f'HTTP {response.status_code}',
                    'details': response.text[:100] if response.text else 'No response'
                }
                logger.error(f"Ошибка API детекции: {response.status_code}")
                self.on_error(Exception(f"API returned {response.status_code}"))
                return result
                
        except (Timeout, ConnectionError) as e:
            result = {
                'status': 'connection_error',
                'error': 'Cannot connect to NSFW detection service',
                'details': str(e)
            }
            logger.warning(f"Не удалось подключиться к сервису детекции: {e}")
            self.on_error(e)
            return result
            
        except Exception as e:
            result = {
                'status': 'error',
                'error': str(e)
            }
            logger.error(f"Ошибка при обращении к сервису детекции: {e}")
            self.on_error(e)
            return result
            
    def get_schedule_time(self):
        """Получить время запуска по расписанию"""
        return self.schedule_time 