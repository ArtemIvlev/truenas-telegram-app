from app.handlers.base_handler import BaseHandler
from app.config.settings import settings
from app.scheduler.scheduler import logger
from app.nsfw.detector import get_nsfw_detector

class DetectNudeHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.schedule_time = settings.DETECT_NUDE_SCHEDULE
        self.detector = get_nsfw_detector()
        
    async def handle(self):
        """Обработка задачи детекции NSFW контента"""
        self.before_run()
        
        try:
            logger.info("Начало обработки изображений на NSFW контент")
            
            # Запускаем обработку всех изображений
            result = await self.detector.process_all_images()
            
            if result['status'] == 'success':
                logger.info(f"Обработка завершена успешно: {result['processed']} обработано, {result['moved_to_review']} перемещено в review")
                self.after_run(result)
                return result
            else:
                logger.error(f"Ошибка при обработке изображений: {result}")
                self.on_error(Exception(f"Processing failed: {result}"))
                return result
                
        except Exception as e:
            logger.error(f"Неожиданная ошибка при обработке NSFW: {str(e)}")
            self.on_error(e)
            return {'status': 'error', 'error': str(e)}
            
    def get_schedule_time(self):
        """Получить время запуска по расписанию"""
        return self.schedule_time 