"""
Headcorn Mockup - AI-генератор мокапов
Главный файл приложения
"""

import streamlit as st
import os
import sys

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорты модулей
from ui.single_generation import single_generation_interface
from ui.batch_processing import batch_processing_interface
from ui.image_upload import image_upload_interface, batch_image_upload_interface
from ui.display_results import display_results
from ui.gallery_stats import show_storage_info, get_all_mockups_data, show_gallery_statistics
from services.upload_services import upload_to_server, upload_to_ftp, get_server_mockups, get_ftp_mockups

# Импорты для генераторов
from mockup_generator import MockupGenerator
from batch_processor import BatchProcessor

def get_mockup_generator():
    """Получение экземпляра генератора мокапов"""
    if "mockup_generator" not in st.session_state:
        st.session_state.mockup_generator = MockupGenerator()
    return st.session_state.mockup_generator

def get_batch_processor():
    """Получение экземпляра процессора пакетной обработки"""
    if "batch_processor" not in st.session_state:
        st.session_state.batch_processor = BatchProcessor()
    return st.session_state.batch_processor

def clear_batch_processor_cache():
    """Очистка кэша процессора пакетной обработки"""
    if "batch_processor" in st.session_state:
        del st.session_state.batch_processor

def main():
    """Главная функция приложения"""
    
    # Настройка страницы
    st.set_page_config(
        page_title="Headcorn Mockup",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Упрощенный заголовок
    st.markdown("### Headcorn Mockup")
    
    # Боковая панель
    with st.sidebar:
        st.markdown("### Навигация")
        
        # Выбор страницы
        page = st.selectbox(
            "Выберите раздел",
            ["Генерация мокапов", "Пакетная обработка", "Информация о хранилищах"],
            help="Выберите нужный раздел приложения"
        )
        
        st.markdown("---")
        
        # Информация о приложении
        st.markdown("### О приложении")
        st.markdown("""
        **Headcorn Mockup** - это AI-генератор мокапов для товаров с логотипами.
        
        **Возможности:**
        - Генерация мокапов с помощью AI
        - Пакетная обработка коллекций
        - Загрузка на FTP и сервер
        - Оптимизация изображений
        """)
    
    # Обработка перегенерации
    if "regenerate_params" in st.session_state:
        from ui.display_results import regenerate_mockup_dynamically
        regenerate_params = st.session_state.regenerate_params
        regenerate_mockup_dynamically(
            regenerate_params["mockup_index"],
            regenerate_params["original_mockup"],
            regenerate_params["original_result"],
            regenerate_params["container_key"]
        )
        # Очищаем параметры после обработки
        del st.session_state.regenerate_params
        return
    
    # Основной контент
    if page == "Генерация мокапов":
        # Загрузка изображений
        image_upload_interface()
        
        st.markdown("---")
        
        # Генерация мокапов
        single_generation_interface()
        
    elif page == "Пакетная обработка":
        # Загрузка изображений для пакетной обработки
        batch_image_upload_interface()
        
        st.markdown("---")
        
        # Пакетная обработка
        batch_processing_interface()
        
    elif page == "Информация о хранилищах":
        # Информация о хранилищах
        show_storage_info()
        
        st.markdown("---")
        
        # Статистика галереи
        all_mockups = get_all_mockups_data()
        if all_mockups:
            st.subheader("📊 Статистика галереи")
            show_gallery_statistics(all_mockups)
        else:
            st.info("📊 Галерея пуста")

if __name__ == "__main__":
    main()
