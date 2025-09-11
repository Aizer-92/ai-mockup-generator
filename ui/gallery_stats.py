"""
Модуль для отображения статистики и галереи
"""

import streamlit as st
import os
import time
from services.upload_services import get_server_mockups, get_ftp_mockups, get_google_drive_mockups

def show_gallery_statistics(mockups: list):
    """Отображение статистики галереи"""
    
    if not mockups:
        st.info("📊 Галерея пуста")
        return
    
    # Статистика по стилям
    styles = {}
    applications = {}
    
    for mockup in mockups:
        if "metadata" in mockup:
            style = mockup["metadata"].get("mockup_style", "Неизвестно")
            application = mockup["metadata"].get("logo_application", "Неизвестно")
            
            styles[style] = styles.get(style, 0) + 1
            applications[application] = applications.get(application, 0) + 1
    
    # Отображаем статистику
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📊 Статистика по стилям:**")
        for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {style}: {count}")
    
    with col2:
        st.write("**📊 Статистика по типам нанесения:**")
        for app, count in sorted(applications.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {app}: {count}")

def get_all_mockups_data():
    """Получение всех данных мокапов из различных источников"""
    
    all_mockups = []
    
    # Мокапы из session_state
    if "generated_mockups" in st.session_state:
        session_mockups = st.session_state.generated_mockups
        all_mockups.extend(session_mockups)
    
    # Мокапы с сервера
    try:
        server_mockups = get_server_mockups(50)
        all_mockups.extend(server_mockups)
    except Exception as e:
        st.warning(f"⚠️ Ошибка получения мокапов с сервера: {e}")
    
    # Мокапы с FTP
    try:
        ftp_mockups = get_ftp_mockups(50)
        all_mockups.extend(ftp_mockups)
    except Exception as e:
        st.warning(f"⚠️ Ошибка получения мокапов с FTP: {e}")
    
    # Мокапы из Google Drive (отключено)
    try:
        gdrive_mockups = get_google_drive_mockups(50)
        all_mockups.extend(gdrive_mockups)
    except Exception as e:
        st.warning(f"⚠️ Ошибка получения мокапов из Google Drive: {e}")
    
    return all_mockups

def show_storage_info():
    """Отображение информации о хранилищах"""
    
    st.subheader("💾 Информация о хранилищах")
    
    # Проверяем доступность хранилищ
    storage_info = []
    
    # Session state
    if "generated_mockups" in st.session_state:
        session_mockups = st.session_state.generated_mockups
        storage_info.append(f"память сессии ({len(session_mockups)} мокапов)")
    
    # Сервер
    try:
        server_mockups = get_server_mockups(10)
        storage_info.append(f"сервер ({len(server_mockups)} мокапов)")
    except:
        storage_info.append("сервер (недоступен)")
    
    # FTP
    try:
        ftp_mockups = get_ftp_mockups(10)
        storage_info.append(f"FTP ({len(ftp_mockups)} мокапов)")
    except:
        storage_info.append("FTP (недоступен)")
    
    # Google Drive (отключено)
    storage_info.append("Google Drive (отключен)")
    
    if storage_info:
        st.info(f"💡 Изображения сохраняются в: {', '.join(storage_info)}")
    
