import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, List
import random
from datetime import datetime

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False

from app.config.settings import settings

logger = logging.getLogger(__name__)

class TelegramPoster:
    """Класс для публикации фотографий в Telegram"""
    
    def __init__(self):
        self.client = None
        self.session_file = 'telegram_session'
        
    async def init_client(self):
        """Инициализация Telegram клиента"""
        if not HAS_TELETHON:
            logger.error("telethon не установлен. Установите: pip install telethon")
            return False
            
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN не настроен")
            return False
            
        try:
            # Для бота используем bot token
            api_id = int(settings.TELEGRAM_API_ID) if settings.TELEGRAM_API_ID else 0
            api_hash = settings.TELEGRAM_API_HASH or ''
            
            if api_id and api_hash:
                self.client = TelegramClient(self.session_file, api_id, api_hash)
                await self.client.start(bot_token=settings.TELEGRAM_BOT_TOKEN)
            else:
                logger.warning("API_ID и API_HASH не настроены, используется заглушка")
                return False
                
            logger.info("Telegram клиент успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Telegram клиента: {e}")
            return False
    
    async def get_random_photos(self, count: int = 1) -> List[Path]:
        """Получить случайные фотографии из директории"""
        photo_dir = Path(settings.PHOTO_DIR)
        
        if not photo_dir.exists():
            logger.error(f"Директория с фото не существует: {photo_dir}")
            return []
        
        # Поддерживаемые форматы
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        # Найти все изображения
        photos = []
        for ext in image_extensions:
            photos.extend(photo_dir.rglob(f'*{ext}'))
            photos.extend(photo_dir.rglob(f'*{ext.upper()}'))
        
        if not photos:
            logger.warning(f"Не найдено фотографий в директории: {photo_dir}")
            return []
        
        # Выбрать случайные фото
        selected = random.sample(photos, min(count, len(photos)))
        logger.info(f"Выбрано {len(selected)} фотографий из {len(photos)} доступных")
        
        return selected
    
    async def post_photo(self, photo_path: Path, caption: Optional[str] = None) -> Dict:
        """Опубликовать фотографию в Telegram"""
        if not self.client:
            logger.error("Telegram клиент не инициализирован")
            return {'status': 'error', 'error': 'client_not_initialized'}
        
        try:
            chat_id = settings.TELEGRAM_CHAT_ID
            if not chat_id:
                logger.error("TELEGRAM_CHAT_ID не настроен")
                return {'status': 'error', 'error': 'chat_id_not_configured'}
            
            # Проверяем размер файла
            file_size = photo_path.stat().st_size
            max_size = 50 * 1024 * 1024  # 50MB лимит Telegram
            
            if file_size > max_size:
                logger.error(f"Файл слишком большой: {file_size} bytes > {max_size} bytes")
                return {'status': 'error', 'error': 'file_too_large'}
            
            # Отправляем фото
            message = await self.client.send_file(
                entity=chat_id,
                file=str(photo_path),
                caption=caption or f"📸 {photo_path.name}",
            )
            
            logger.info(f"Фото успешно отправлено: {photo_path.name}")
            return {
                'status': 'success',
                'message_id': message.id,
                'photo_name': photo_path.name,
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Ошибка отправки фото {photo_path.name}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def post_random_photo(self, caption: Optional[str] = None) -> Dict:
        """Опубликовать случайную фотографию"""
        photos = await self.get_random_photos(1)
        
        if not photos:
            return {'status': 'error', 'error': 'no_photos_found'}
        
        photo = photos[0]
        result = await self.post_photo(photo, caption)
        
        return result
    
    async def close(self):
        """Закрыть соединение с Telegram"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram клиент отключен")

# Глобальный экземпляр
_telegram_poster = None

async def get_telegram_poster() -> TelegramPoster:
    """Получить глобальный экземпляр TelegramPoster"""
    global _telegram_poster
    
    if _telegram_poster is None:
        _telegram_poster = TelegramPoster()
        await _telegram_poster.init_client()
    
    return _telegram_poster

async def post_random_photo(caption: Optional[str] = None) -> Dict:
    """Функция для публикации случайной фотографии (совместимость с предыдущим кодом)"""
    try:
        poster = await get_telegram_poster()
        return await poster.post_random_photo(caption)
    except Exception as e:
        logger.error(f"Ошибка в post_random_photo: {e}")
        return {'status': 'error', 'error': str(e)}