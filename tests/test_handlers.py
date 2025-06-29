import pytest
from unittest.mock import Mock, patch
import requests
from app.handlers.detect_nude_handler import DetectNudeHandler
from app.handlers.random_time_handler import RandomTimeHandler
from app.config.settings import settings


class TestDetectNudeHandler:
    """Тесты для DetectNudeHandler"""
    
    def test_init(self):
        """Тест инициализации обработчика"""
        handler = DetectNudeHandler()
        assert handler.api_url == settings.DETECT_NUDE_API_URL
        assert handler.timeout == settings.REQUEST_TIMEOUT
        assert handler.max_retries == settings.MAX_RETRIES
    
    @patch('app.handlers.detect_nude_handler.requests.post')
    def test_handle_success(self, mock_post):
        """Тест успешного выполнения задачи"""
        # Настройка mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "completed"}'
        mock_post.return_value = mock_response
        
        # Выполнение
        handler = DetectNudeHandler()
        result = handler.handle()
        
        # Проверки
        assert result['status'] == 'success'
        assert result['response'] == '{"status": "completed"}'
        assert result['attempt'] == 1
        mock_post.assert_called_once()
    
    @patch('app.handlers.detect_nude_handler.requests.post')
    def test_handle_timeout_retry(self, mock_post):
        """Тест retry при таймауте"""
        # Настройка mock для таймаута
        mock_post.side_effect = requests.exceptions.Timeout()
        
        # Выполнение
        handler = DetectNudeHandler()
        handler.max_retries = 2  # Уменьшаем для быстрого теста
        result = handler.handle()
        
        # Проверки
        assert result['status'] == 'error'
        assert result['error'] == 'timeout'
        assert result['attempts'] == 2
        assert mock_post.call_count == 2
    
    @patch('app.handlers.detect_nude_handler.requests.post')
    def test_handle_http_error(self, mock_post):
        """Тест обработки HTTP ошибки"""
        # Настройка mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        # Выполнение
        handler = DetectNudeHandler()
        handler.max_retries = 1
        result = handler.handle()
        
        # Проверки
        assert result['status'] == 'error'
        assert result['error'] == 'max_retries_exceeded'


class TestRandomTimeHandler:
    """Тесты для RandomTimeHandler"""
    
    def test_init(self):
        """Тест инициализации обработчика"""
        handler = RandomTimeHandler()
        assert handler.base_time == settings.RANDOM_TIME_BASE
        assert handler.duration_minutes == settings.RANDOM_TIME_DURATION
    
    @pytest.mark.asyncio
    async def test_post_random_photo_stub(self):
        """Тест заглушки для публикации фото"""
        handler = RandomTimeHandler()
        result = await handler._post_random_photo_stub()
        
        assert result['status'] == 'success'
        assert 'Photo posted (stub)' in result['message']
    
    def test_handle_scheduling(self):
        """Тест планирования задачи"""
        handler = RandomTimeHandler()
        result = handler.handle()
        
        # Проверяем что задача запланирована
        assert result['status'] == 'success'
        assert 'scheduled_time' in result
        assert 'delay_seconds' in result


@pytest.fixture
def mock_settings():
    """Фикстура для мокания настроек"""
    with patch('app.config.settings.settings') as mock:
        mock.DETECT_NUDE_API_URL = 'http://test.example.com/api'
        mock.REQUEST_TIMEOUT = 10
        mock.MAX_RETRIES = 2
        mock.RETRY_DELAY = 1
        mock.RANDOM_TIME_BASE = '09:00'
        mock.RANDOM_TIME_DURATION = 30
        yield mock