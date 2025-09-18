"""
Конфигурация для AI Mockup Generator
"""
import os
from dotenv import load_dotenv

# Загружаем .env файл для локальной разработки
load_dotenv()
# Также загружаем FTP конфигурацию
load_dotenv('ftp_config.env')

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

# Google Drive настройки (отключены)
GOOGLE_DRIVE_ENABLED = False
GOOGLE_DRIVE_FOLDER_NAME = 'AI Mockup Generator'

# Серверное хранилище настройки
SERVER_STORAGE_ENABLED = os.getenv('SERVER_STORAGE_ENABLED', 'true').lower() == 'true'
SERVER_STORAGE_PATH = os.getenv('SERVER_STORAGE_PATH', 'mockups')
SERVER_WEB_URL = os.getenv('SERVER_WEB_URL', 'http://search.headcorn.pro/mockups')

# FTP настройки
FTP_ENABLED = os.getenv('FTP_ENABLED', 'true').lower() == 'true'
FTP_HOST = os.getenv('FTP_HOST', '')
FTP_USERNAME = os.getenv('FTP_USERNAME', '')
FTP_PASSWORD = os.getenv('FTP_PASSWORD', '')
FTP_REMOTE_PATH = os.getenv('FTP_REMOTE_PATH', '/mockups')
GEMINI_MODEL = 'gemini-2.5-flash-image-preview'  # Официальная модель для генерации изображений
GEMINI_ANALYSIS_MODEL = 'gemini-2.0-flash-exp'  # Современная модель для анализа коллекций

# Настройки изображений (ОПТИМИЗИРОВАННЫЕ для экономии API токенов)
MAX_IMAGE_SIZE = (384, 384)  # Оптимизированный размер для экономии API токенов (-25% токенов)
COMPRESSION_QUALITY = 60  # Более агрессивное сжатие (-15% токенов)
LOGO_MAX_SIZE = (128, 128)  # Оптимизированный размер логотипа (-30% токенов)

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

# Оптимизации (можно отключить для отладки)
UNIFIED_ANALYSIS_ENABLED = True  # Объединенный анализ в креативном генераторе
PDF_COMPRESSION_ENABLED = True   # Сжатие PDF файлов

# Настройки аутентификации уже определены выше
