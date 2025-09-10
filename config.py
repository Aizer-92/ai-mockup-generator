"""
Конфигурация для AI Mockup Generator
"""
import os
from dotenv import load_dotenv

# Загружаем .env файл для локальной разработки
load_dotenv()

# Функция для получения конфигурации
def get_config():
    """Получает конфигурацию из secrets или переменных окружения"""
    try:
        import streamlit as st
        # Если мы в Streamlit Cloud, используем secrets
        if hasattr(st, 'secrets') and st.secrets:
            return {
                'GEMINI_API_KEY': st.secrets.get('GEMINI_API_KEY', os.getenv('GEMINI_API_KEY')),
                'AUTH_ENABLED': st.secrets.get('AUTH_ENABLED', os.getenv('AUTH_ENABLED', 'true')).lower() == 'true',
                'AUTH_PASSWORD': st.secrets.get('AUTH_PASSWORD', os.getenv('AUTH_PASSWORD', 'admin123'))
            }
    except:
        pass
    
    # Локальная разработка или fallback
    return {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'AUTH_ENABLED': os.getenv('AUTH_ENABLED', 'true').lower() == 'true',
        'AUTH_PASSWORD': os.getenv('AUTH_PASSWORD', 'admin123')
    }

# Получаем конфигурацию
config = get_config()
GEMINI_API_KEY = config['GEMINI_API_KEY']
AUTH_ENABLED = config['AUTH_ENABLED']
AUTH_PASSWORD = config['AUTH_PASSWORD']

# Google Drive настройки
GOOGLE_DRIVE_ENABLED = config.get('GOOGLE_DRIVE_ENABLED', 'false').lower() == 'true'
GOOGLE_DRIVE_FOLDER_NAME = config.get('GOOGLE_DRIVE_FOLDER_NAME', 'AI Mockup Generator')

# Серверное хранилище настройки
SERVER_STORAGE_ENABLED = config.get('SERVER_STORAGE_ENABLED', 'true').lower() == 'true'
SERVER_STORAGE_PATH = config.get('SERVER_STORAGE_PATH', 'mockups')
SERVER_WEB_URL = config.get('SERVER_WEB_URL', 'http://localhost:8501/static/mockups')

# FTP настройки
FTP_ENABLED = config.get('FTP_ENABLED', 'true').lower() == 'true'
FTP_HOST = config.get('FTP_HOST', '')
FTP_USERNAME = config.get('FTP_USERNAME', '')
FTP_PASSWORD = config.get('FTP_PASSWORD', '')
FTP_REMOTE_PATH = config.get('FTP_REMOTE_PATH', '/mockups')
GEMINI_MODEL = 'gemini-2.5-flash-image-preview'  # Официальная модель для генерации изображений
GEMINI_ANALYSIS_MODEL = 'gemini-2.0-flash-exp'  # Современная модель для анализа коллекций

# Настройки изображений (ЭКОНОМНЫЕ для сохранения лимитов API)
MAX_IMAGE_SIZE = (512, 512)  # Уменьшенный размер для экономии API токенов
COMPRESSION_QUALITY = 70  # Более агрессивное сжатие
LOGO_MAX_SIZE = (150, 150)  # Уменьшенный размер логотипа

# Пути
UPLOAD_DIR = 'uploads'
OUTPUT_DIR = 'outputs'
CACHE_DIR = 'cache'
TEMPLATES_DIR = 'templates'

# Кэширование
CACHE_ENABLED = True
CACHE_EXPIRY_HOURS = 24

# Веб-интерфейс
STREAMLIT_PORT = 8501
STREAMLIT_HOST = 'localhost'

# Экономичные настройки (МАКСИМАЛЬНО ЭКОНОМНЫЕ)
BATCH_SIZE = 1  # Только один вариант за запрос для экономии
MAX_CONCURRENT_REQUESTS = 1  # Только один запрос одновременно

# Настройки аутентификации уже определены выше
