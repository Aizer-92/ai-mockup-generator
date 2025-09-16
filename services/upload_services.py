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
        
        # Сжатие и загрузка на FTP (без уведомлений)
        from ftp_uploader import get_ftp_uploader
        ftp_uploader = get_ftp_uploader()
        if not ftp_uploader:
            return
        
        # Загружаем сжатое изображение на FTP
        filename = ftp_uploader.upload_mockup(compressed_data, metadata, description)
        
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
        
        # Получаем список файлов
        files = ftp_uploader.list_files()
        
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
