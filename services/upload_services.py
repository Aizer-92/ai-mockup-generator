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
    """Загрузка изображения на FTP сервер"""
    try:
        if not config.FTP_ENABLED:
            return
        
        ftp_uploader = FTPUploader()
        
        # Подключаемся к FTP
        if not ftp_uploader.connect():
            st.warning("⚠️ Не удалось подключиться к FTP серверу")
            return
        
        # Создаем имя файла
        timestamp = int(time.time())
        filename = f"mockup_{timestamp}.jpg"
        
        # Загружаем на FTP
        success = ftp_uploader.upload_image(image_data, filename, metadata)
        
        if success:
            st.success(f"✅ Изображение загружено на FTP: {filename}")
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
        
        ftp_uploader = FTPUploader()
        
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
