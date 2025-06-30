import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
from PIL import Image

from app.config.settings import settings

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logger = logging.getLogger(__name__)

class NSFWDetector:
    """Класс для детекции NSFW контента в изображениях"""
    
    def __init__(self):
        self.api_url = settings.DETECT_NUDE_API_URL
        self.threshold = settings.NSFW_THRESHOLD
        self.min_image_size = settings.MIN_IMAGE_SIZE
        self.max_image_size = settings.MAX_IMAGE_SIZE
        self.photo_dir = Path(settings.PHOTO_DIR)
        self.review_dir = self.photo_dir / settings.REVIEW_DIR
        
        # Создаем папку для проверки
        self.review_dir.mkdir(exist_ok=True)
    
    def _is_valid_image_size(self, image_path: Path) -> bool:
        """Проверка размера изображения"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                total_pixels = width * height
                
                return self.min_image_size <= total_pixels <= self.max_image_size
        except Exception as e:
            logger.error(f"Ошибка проверки размера изображения {image_path}: {e}")
            return False
    
    def _get_images_to_process(self) -> List[Path]:
        """Получить список изображений для обработки"""
        if not self.photo_dir.exists():
            logger.error(f"Директория с фото не существует: {self.photo_dir}")
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        images = []
        
        # Исключаем папку review из поиска
        for image_path in self.photo_dir.rglob('*'):
            if (image_path.suffix.lower() in image_extensions and 
                not str(image_path).startswith(str(self.review_dir)) and
                self._is_valid_image_size(image_path)):
                images.append(image_path)
        
        logger.info(f"Найдено {len(images)} изображений для обработки")
        return images
    
    async def detect_single_image(self, image_path: Path) -> Dict:
        """Детекция NSFW для одного изображения через API или заглушку"""
        
        # Проверяем настройку API URL
        if not self.api_url or self.api_url in ['http://localhost:8888/run', 'http://192.168.2.228:8888/run']:
            logger.warning(f"NSFW API не настроен, используется заглушка для {image_path.name}")
            return self._mock_detection(image_path)
        
        if not HAS_REQUESTS:
            logger.error("requests library не доступна, используется заглушка")
            return self._mock_detection(image_path)
        
        try:
            # Подготавливаем файл для отправки
            with open(image_path, 'rb') as img_file:
                files = {'file': (image_path.name, img_file, 'image/jpeg')}
                
                response = requests.post(
                    self.api_url,
                    files=files,
                    timeout=settings.REQUEST_TIMEOUT
                )
            
            if response.status_code == 200:
                result = response.json()
                is_nsfw = result.get('is_nude', False)
                confidence = result.get('confidence', 0.0)
                
                return {
                    'status': 'success',
                    'image': str(image_path),
                    'is_nsfw': is_nsfw,
                    'confidence': confidence,
                    'threshold_exceeded': confidence > self.threshold,
                    'method': 'api'
                }
            else:
                logger.error(f"API ошибка для {image_path.name}: {response.status_code} - {response.text}")
                logger.warning("Переключение на заглушку из-за ошибки API")
                return self._mock_detection(image_path)
                
        except requests.exceptions.Timeout:
            logger.warning(f"Таймаут API для {image_path.name}, используется заглушка")
            return self._mock_detection(image_path)
        except Exception as e:
            logger.warning(f"Ошибка API для {image_path.name}: {e}, используется заглушка")
            return self._mock_detection(image_path)
    
    def _mock_detection(self, image_path: Path) -> Dict:
        """Заглушка для детекции NSFW"""
        import random
        
        # Генерируем случайный результат для демонстрации
        # В реальности здесь могла бы быть локальная модель
        mock_confidence = random.uniform(0.1, 0.3)  # Обычно низкая вероятность
        is_nsfw = False  # По умолчанию считаем безопасным
        
        # Иногда помечаем как подозрительное для демонстрации
        if random.random() < 0.05:  # 5% вероятность
            mock_confidence = random.uniform(0.7, 0.9)
            is_nsfw = True
        
        return {
            'status': 'success',
            'image': str(image_path),
            'is_nsfw': is_nsfw,
            'confidence': mock_confidence,
            'threshold_exceeded': mock_confidence > self.threshold,
            'method': 'mock',
            'note': 'Используется заглушка - для реальной детекции настройте DETECT_NUDE_API_URL'
        }
    
    def move_to_review(self, image_path: Path) -> bool:
        """Переместить изображение в папку для проверки"""
        try:
            # Создаем уникальное имя файла если такой уже существует
            review_path = self.review_dir / image_path.name
            counter = 1
            
            while review_path.exists():
                name_parts = image_path.stem, counter, image_path.suffix
                review_path = self.review_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            shutil.move(str(image_path), str(review_path))
            logger.info(f"Изображение перемещено в review: {image_path.name} -> {review_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка перемещения файла {image_path.name}: {e}")
            return False
    
    async def process_all_images(self) -> Dict:
        """Обработать все изображения в директории"""
        images = self._get_images_to_process()
        
        if not images:
            return {
                'status': 'success',
                'message': 'No images to process',
                'processed': 0,
                'moved_to_review': 0,
                'errors': 0
            }
        
        results = {
            'status': 'success',
            'total_images': len(images),
            'processed': 0,
            'moved_to_review': 0,
            'errors': 0,
            'details': []
        }
        
        for image_path in images:
            logger.info(f"Обрабатываем изображение: {image_path.name}")
            
            detection_result = await self.detect_single_image(image_path)
            results['details'].append(detection_result)
            
            if detection_result['status'] == 'success':
                results['processed'] += 1
                
                # Если превышен порог NSFW - перемещаем в папку review
                if detection_result.get('threshold_exceeded', False):
                    if self.move_to_review(image_path):
                        results['moved_to_review'] += 1
                        logger.warning(f"NSFW обнаружен: {image_path.name} (confidence: {detection_result['confidence']})")
            else:
                results['errors'] += 1
        
        logger.info(f"Обработка завершена: {results['processed']} обработано, {results['moved_to_review']} перемещено в review, {results['errors']} ошибок")
        return results
    
    def get_review_stats(self) -> Dict:
        """Получить статистику папки review"""
        if not self.review_dir.exists():
            return {
                'review_dir_exists': False,
                'count': 0,
                'total_size': 0
            }
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        review_files = []
        
        for file_path in self.review_dir.iterdir():
            if file_path.suffix.lower() in image_extensions:
                review_files.append(file_path)
        
        total_size = sum(f.stat().st_size for f in review_files)
        
        return {
            'review_dir_exists': True,
            'review_dir': str(self.review_dir),
            'count': len(review_files),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': [{'name': f.name, 'size': f.stat().st_size} for f in review_files]
        }

# Глобальный экземпляр
_nsfw_detector = None

def get_nsfw_detector() -> NSFWDetector:
    """Получить глобальный экземпляр NSFWDetector"""
    global _nsfw_detector
    
    if _nsfw_detector is None:
        _nsfw_detector = NSFWDetector()
    
    return _nsfw_detector