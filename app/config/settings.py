import os
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings:
    """Централизованные настройки приложения"""
    
    # API URLs
    DETECT_NUDE_API_URL: str = os.getenv('DETECT_NUDE_API_URL', 'http://localhost:8888/run')
    TELEGRAM_API_URL: str = os.getenv('TELEGRAM_API_URL', 'https://api.telegram.org')
    
    # Schedules
    DETECT_NUDE_SCHEDULE: str = os.getenv('DETECT_NUDE_SCHEDULE', '0 3 * * *')
    RANDOM_TIME_SCHEDULE: str = os.getenv('RANDOM_TIME_SCHEDULE', '0 8 * * *')
    
    # Random time settings
    RANDOM_TIME_BASE: str = os.getenv('RANDOM_TIME_BASE', '08:00')
    RANDOM_TIME_DURATION: int = int(os.getenv('RANDOM_TIME_DURATION', '59'))
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv('TELEGRAM_CHAT_ID')
    
    # File paths
    PHOTO_DIR: str = os.getenv('PHOTO_DIR', '/mnt/smb/OneDrive/Pictures/!Фотосессии/')
    DB_FILE: str = os.getenv('DB_FILE', '/app/data/photos.db')
    REVIEW_DIR: str = os.getenv('REVIEW_DIR', 'review')
    TELEGRAM_DB: str = os.getenv('TELEGRAM_DB', '/app/data/telegram_bot.db')
    TABLE_NAME: str = os.getenv('TABLE_NAME', 'photos_ok')
    
    # Thresholds
    NSFW_THRESHOLD: float = float(os.getenv('NSFW_THRESHOLD', '0.8'))
    CLIP_THRESHOLD: float = float(os.getenv('CLIP_THRESHOLD', '0.8'))
    MIN_IMAGE_SIZE: int = int(os.getenv('MIN_IMAGE_SIZE', '2500'))
    MAX_IMAGE_SIZE: int = int(os.getenv('MAX_IMAGE_SIZE', '10000'))
    
    # App settings
    APP_VERSION: str = os.getenv('APP_VERSION', 'development')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Request settings
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY: int = int(os.getenv('RETRY_DELAY', '5'))

    def validate(self) -> bool:
        """Валидация критически важных настроек"""
        required_settings = []
        
        if not self.TELEGRAM_BOT_TOKEN:
            required_settings.append('TELEGRAM_BOT_TOKEN')
        
        if not self.TELEGRAM_CHAT_ID:
            required_settings.append('TELEGRAM_CHAT_ID')
            
        if required_settings:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(required_settings)}")
        
        return True

# Создаем глобальный экземпляр настроек
settings = Settings()