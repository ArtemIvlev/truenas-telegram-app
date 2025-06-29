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
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
        
    def handle(self):
        """Обработка задачи детекции NSFW контента с retry механизмом"""
        self.before_run()
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Отправка запроса на detect_nude сервис (попытка {attempt})")
                
                response = requests.post(
                    self.api_url,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = {
                        'status': 'success',
                        'response': response.text,
                        'attempt': attempt
                    }
                    logger.info(f"detect_nude сервис успешно выполнен (попытка {attempt})")
                    if response.text:
                        logger.info(f"Ответ сервиса: {response.text}")
                    
                    self.after_run(result)
                    return result
                else:
                    logger.warning(f"HTTP ошибка {response.status_code} на попытке {attempt}: {response.text}")
                    
            except Timeout:
                logger.warning(f"Таймаут запроса на попытке {attempt}")
                if attempt == self.max_retries:
                    error = TimeoutError(f"Таймаут после {self.max_retries} попыток")
                    self.on_error(error)
                    return {'status': 'error', 'error': 'timeout', 'attempts': attempt}
                    
            except ConnectionError:
                logger.warning(f"Ошибка подключения на попытке {attempt}")
                if attempt == self.max_retries:
                    error = ConnectionError(f"Ошибка подключения после {self.max_retries} попыток")
                    self.on_error(error)
                    return {'status': 'error', 'error': 'connection_error', 'attempts': attempt}
                    
            except RequestException as e:
                logger.warning(f"Ошибка HTTP запроса на попытке {attempt}: {str(e)}")
                if attempt == self.max_retries:
                    self.on_error(e)
                    return {'status': 'error', 'error': str(e), 'attempts': attempt}
                    
            except Exception as e:
                logger.error(f"Неожиданная ошибка на попытке {attempt}: {str(e)}")
                self.on_error(e)
                return {'status': 'error', 'error': str(e), 'attempts': attempt}
            
            # Ждем перед следующей попыткой, если это не последняя попытка
            if attempt < self.max_retries:
                logger.info(f"Ожидание {self.retry_delay} секунд перед следующей попыткой")
                time.sleep(self.retry_delay)
        
        # Если все попытки исчерпаны
        error = RuntimeError(f"Все {self.max_retries} попыток исчерпаны")
        self.on_error(error)
        return {'status': 'error', 'error': 'max_retries_exceeded', 'attempts': self.max_retries}
            
    def get_schedule_time(self):
        """Получить время запуска по расписанию"""
        return self.schedule_time 