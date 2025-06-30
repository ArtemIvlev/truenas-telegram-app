import os
from app.handlers.base_handler import BaseHandler
from app.config.settings import settings
from app.scheduler.scheduler import logger

class FileCheckHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.api_url = settings.TRUENAS_API_URL
        self.api_key = settings.TRUENAS_API_KEY
        self.schedule_time = settings.FILE_CHECK_SCHEDULE
        self.config = {
            'storage_path': '/data',
            'limit': 10
        }
        
    def handle(self):
        storage_path = self.config.get('storage_path', '/data')
        limit = self.config.get('limit', 10)
        
        try:
            files = []
            for item in os.listdir(storage_path):
                if os.path.isfile(os.path.join(storage_path, item)):
                    files.append(item)
                if len(files) >= limit:
                    break
                    
            return {
                'status': 'success',
                'files': files
            }
        except Exception as e:
            logger.error(f"Ошибка при чтении директории: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def get_schedule_time(self):
        """Получить время запуска по расписанию"""
        return self.schedule_time 