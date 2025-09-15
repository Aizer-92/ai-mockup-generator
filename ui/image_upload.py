"""
Модуль для загрузки изображений
"""

import streamlit as st
from PIL import Image
from image_processor import ImageProcessor

def image_upload_interface():
    """Интерфейс загрузки изображений"""
    
    st.subheader("📁 Загрузка изображений")
    
    # Загрузка изображения товара
    st.write("**📦 Изображение товара:**")
    product_image = st.file_uploader(
        "Выберите изображение товара",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Загрузите изображение товара для генерации мокапа"
    )
    
    if product_image is not None:
        try:
            # Конвертируем в RGB если нужно
            image = Image.open(product_image)
            if image.mode in ('RGBA', 'LA', 'P'):
                processor = ImageProcessor()
                image = processor.convert_to_rgb(image)
            
            # Сохраняем в session_state
            st.session_state.product_image = image
            st.success("✅ Изображение товара загружено")
            
            # Показываем превью
            st.image(image, width=200, caption="Превью товара")
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки изображения товара: {e}")
    
    # Загрузка логотипа
    st.write("**🏷️ Логотип:**")
    logo_image = st.file_uploader(
        "Выберите логотип",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Загрузите логотип для нанесения на товар"
    )
    
    if logo_image is not None:
        try:
            # Конвертируем в RGB если нужно
            image = Image.open(logo_image)
            if image.mode in ('RGBA', 'LA', 'P'):
                processor = ImageProcessor()
                image = processor.convert_to_rgb(image)
            
            # Сохраняем в session_state
            st.session_state.logo_image = image
            st.success("✅ Логотип загружен")
            
            # Показываем превью
            st.image(image, width=200, caption="Превью логотипа")
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки логотипа: {e}")
    
    # Загрузка паттерна (опционально)
    st.write("**🎨 Паттерн (опционально):**")
    pattern_image = st.file_uploader(
        "Выберите паттерн",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Загрузите паттерн для создания повторяющегося рисунка"
    )
    
    if pattern_image is not None:
        try:
            # Конвертируем в RGB если нужно
            image = Image.open(pattern_image)
            if image.mode in ('RGBA', 'LA', 'P'):
                processor = ImageProcessor()
                image = processor.convert_to_rgb(image)
            
            # Сохраняем в session_state
            st.session_state.pattern_image = image
            st.success("✅ Паттерн загружен")
            
            # Показываем превью
            st.image(image, width=200, caption="Превью паттерна")
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки паттерна: {e}")

def batch_image_upload_interface():
    """Интерфейс загрузки изображений для пакетной обработки"""
    
    st.subheader("📁 Загрузка изображений для пакетной обработки")
    
    # Загрузка изображений товаров
    st.write("**📦 Изображения товаров:**")
    product_images = st.file_uploader(
        "Выберите изображения товаров",
        type=['jpg', 'jpeg', 'png', 'webp'],
        accept_multiple_files=True,
        help="Загрузите несколько изображений товаров для создания коллекции"
    )
    
    if product_images:
        try:
            processed_images = []
            for i, img in enumerate(product_images):
                # Конвертируем в RGB если нужно
                image = Image.open(img)
                if image.mode in ('RGBA', 'LA', 'P'):
                    processor = ImageProcessor()
                    image = processor.convert_to_rgb(image)
                
                processed_images.append(image)
            
            # Сохраняем в session_state
            st.session_state.batch_product_images = processed_images
            st.success(f"✅ Загружено {len(processed_images)} изображений товаров")
            
            # Показываем превью
            cols = st.columns(min(len(processed_images), 4))
            for i, img in enumerate(processed_images):
                with cols[i % 4]:
                    st.image(img, width=100, caption=f"Товар {i+1}")
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки изображений товаров: {e}")
    
    # Загрузка логотипа
    st.write("**🏷️ Логотип для коллекции:**")
    logo_image = st.file_uploader(
        "Выберите логотип",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Загрузите логотип для нанесения на все товары коллекции"
    )
    
    if logo_image is not None:
        try:
            # Конвертируем в RGB если нужно
            image = Image.open(logo_image)
            if image.mode in ('RGBA', 'LA', 'P'):
                processor = ImageProcessor()
                image = processor.convert_to_rgb(image)
            
            # Сохраняем в session_state
            st.session_state.batch_logo_image = image
            st.success("✅ Логотип для коллекции загружен")
            
            # Показываем превью
            st.image(image, width=200, caption="Превью логотипа")
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки логотипа: {e}")
    
    # Загрузка паттерна (опционально)
    st.write("**🎨 Паттерн для коллекции (опционально):**")
    pattern_image = st.file_uploader(
        "Выберите паттерн",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Загрузите паттерн для создания повторяющегося рисунка на всех товарах"
    )
    
    if pattern_image is not None:
        try:
            # Конвертируем в RGB если нужно
            image = Image.open(pattern_image)
            if image.mode in ('RGBA', 'LA', 'P'):
                processor = ImageProcessor()
                image = processor.convert_to_rgb(image)
            
            # Сохраняем в session_state
            st.session_state.batch_pattern_image = image
            st.success("✅ Паттерн для коллекции загружен")
            
            # Показываем превью
            st.image(image, width=200, caption="Превью паттерна")
            
        except Exception as e:
            st.error(f"❌ Ошибка загрузки паттерна: {e}")

