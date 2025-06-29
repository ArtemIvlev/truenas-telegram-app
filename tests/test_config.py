import pytest
import os
from unittest.mock import patch
from app.config.settings import Settings


class TestSettings:
    """Тесты для класса Settings"""
    
    def test_default_values(self):
        """Тест значений по умолчанию"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.DETECT_NUDE_API_URL == 'http://localhost:8888/run'
            assert settings.REQUEST_TIMEOUT == 30
            assert settings.MAX_RETRIES == 3
            assert settings.DEBUG == False
    
    def test_environment_override(self):
        """Тест переопределения через переменные окружения"""
        env_vars = {
            'DETECT_NUDE_API_URL': 'http://custom.api.com',
            'REQUEST_TIMEOUT': '60',
            'MAX_RETRIES': '5',
            'DEBUG': 'true'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.DETECT_NUDE_API_URL == 'http://custom.api.com'
            assert settings.REQUEST_TIMEOUT == 60
            assert settings.MAX_RETRIES == 5
            assert settings.DEBUG == True
    
    def test_validation_missing_required(self):
        """Тест валидации при отсутствии обязательных параметров"""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            with pytest.raises(ValueError) as excinfo:
                settings.validate()
            
            assert 'TELEGRAM_BOT_TOKEN' in str(excinfo.value)
            assert 'TELEGRAM_CHAT_ID' in str(excinfo.value)
    
    def test_validation_success(self):
        """Тест успешной валидации"""
        env_vars = {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'TELEGRAM_CHAT_ID': 'test_chat_id'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.validate() == True