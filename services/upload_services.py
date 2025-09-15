"""
Модуль для загрузки изображений на различные сервисы
"""

import streamlit as st
import time
import os
import config
from ftp_uploader import FTPUploader
from server_storage import ServerStorage

def upload_to_server(image_data: bytes, metadata: dict, description: str = ""):
    """Загрузка изображения на сервер"""
    try:
        if not config.SERVER_STORAGE_ENABLED:
            return
        
        storage = ServerStorage()
        filename = f"mockup_{int(time.time())}.jpg"
        
        # Загружаем на сервер
        success = storage.upload_image(image_data, filename, metadata)
        
        if success:
            st.success(f"✅ Изображение загружено на сервер: {filename}")
        else:
            st.warning("⚠️ Не удалось загрузить изображение на сервер")
            
    except Exception as e:
        st.error(f"❌ Ошибка загрузки на сервер: {e}")

def get_server_mockups(limit: int = 50) -> list:
    """Получение списка мокапов с сервера"""
    try:
        if not config.SERVER_STORAGE_ENABLED:
            return []
        
        storage = ServerStorage()
        return storage.list_images(limit)
        
    except Exception as e:
        st.error(f"❌ Ошибка получения мокапов с сервера: {e}")
        return []

def upload_to_ftp(image_data: bytes, metadata: dict, description: str = ""):
    """Загрузка изображения на FTP сервер с сжатием"""
    try:
        if not config.FTP_ENABLED:
            return
        
        from image_processor import ImageProcessor
        
        # Сжимаем изображение перед загрузкой
        processor = ImageProcessor()
        
        # Конвертируем bytes в PIL Image
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_data))
        
        # Сжимаем изображение (максимум 1200x1200, качество 85%)
        compressed_data = processor.compress_for_ftp(image, max_size=(1200, 1200), quality=85)
        
        # Показываем размеры до и после сжатия
        original_size = processor.get_compressed_size(image_data)
        compressed_size = processor.get_compressed_size(compressed_data)
        st.info(f"📊 Сжатие: {original_size} → {compressed_size}")
        
        from ftp_uploader import get_ftp_uploader
        ftp_uploader = get_ftp_uploader()
        if not ftp_uploader:
            st.warning("⚠️ Не удалось инициализировать FTP загрузчик")
            return
        
        # Подключаемся к FTP
        if not ftp_uploader.connect():
            st.warning("⚠️ Не удалось подключиться к FTP серверу")
            return
        
        # Создаем имя файла
        timestamp = int(time.time())
        filename = f"mockup_{timestamp}.jpg"
        
        # Загружаем сжатое изображение на FTP
        success = ftp_uploader.upload_image(compressed_data, filename, metadata)
        
        if success:
            st.success(f"✅ Изображение загружено на FTP: {filename} ({compressed_size})")
        else:
            st.warning("⚠️ Не удалось загрузить изображение на FTP")
        
        # Закрываем соединение
        ftp_uploader.disconnect()
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки на FTP: {e}")

def get_ftp_mockups(limit: int = 50) -> list:
    """Получение списка мокапов с FTP сервера"""
    try:
        if not config.FTP_ENABLED:
            return []
        
        from ftp_uploader import get_ftp_uploader
        ftp_uploader = get_ftp_uploader()
        if not ftp_uploader:
            st.warning("⚠️ Не удалось инициализировать FTP загрузчик")
            return
        
        # Подключаемся к FTP
        if not ftp_uploader.connect():
            st.warning("⚠️ Не удалось подключиться к FTP серверу")
            return []
        
        # Получаем список файлов
        files = ftp_uploader.list_files(limit)
        
        # Закрываем соединение
        ftp_uploader.disconnect()
        
        return files
        
    except Exception as e:
        st.error(f"❌ Ошибка получения мокапов с FTP: {e}")
        return []

def upload_to_google_drive(image_data: bytes, metadata: dict, description: str = ""):
    """Загрузка изображения в Google Drive (отключено)"""
    pass

def get_google_drive_mockups(limit: int = 50) -> list:
    """Получение списка мокапов из Google Drive (отключено)"""
    return []
