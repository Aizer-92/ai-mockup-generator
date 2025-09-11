"""
Модуль для отображения результатов генерации мокапов
"""

import streamlit as st
import time
from PIL import Image
import io
from image_processor import ImageProcessor

def display_results(result: dict):
    """Отображение результатов генерации с динамическим обновлением"""
    
    # Сохраняем результат в session_state для галереи
    st.session_state.last_result = result
    
    # Сохраняем мокапы в session_state для галереи
    if "generated_mockups" not in st.session_state:
        st.session_state.generated_mockups = []
    
    mockups = result.get("mockups", {})
    
    if not mockups:
        st.error("❌ Нет данных о мокапах для отображения")
        st.error(f"Доступные ключи в результате: {list(result.keys())}")
        return
    
    # Добавляем новые мокапы в session_state
    if "gemini_mockups" in mockups:
        for mockup in mockups["gemini_mockups"]:
            if "image_data" in mockup:
                # Создаем запись для галереи
                gallery_entry = {
                    "image_data": mockup["image_data"],
                    "metadata": {
                        "mockup_style": result.get("style", "Неизвестно"),
                        "logo_application": result.get("logo_application", "Неизвестно"),
                        "logo_placement": result.get("logo_position", "Неизвестно"),
                        "logo_size": result.get("logo_size", "Неизвестно"),
                        "logo_color": result.get("logo_color", "Неизвестно"),
                        "product_color": result.get("product_color", "Неизвестно"),
                        "product_angle": result.get("product_angle", "Неизвестно"),
                        "special_requirements": result.get("custom_prompt", "")
                    },
                    "timestamp": time.time(),
                    "description": mockup.get("description", "")
                }
                
                # Добавляем в session_state (избегаем дублирования)
                if gallery_entry not in st.session_state.generated_mockups:
                    st.session_state.generated_mockups.append(gallery_entry)
    
    # Сначала отображаем мокапы
    display_mockups_dynamically(mockups, result)
    
    # Затем загружаем на серверы (в фоновом режиме)
    if "gemini_mockups" in mockups:
        for mockup in mockups["gemini_mockups"]:
            if "image_data" in mockup:
                gallery_entry = {
                    "image_data": mockup["image_data"],
                    "metadata": {
                        "style": mockup.get("style", "unknown"),
                        "logo_application": mockup.get("logo_application", "unknown"),
                        "custom_prompt": mockup.get("custom_prompt", ""),
                        "product_color": mockup.get("product_color", "белый"),
                        "product_angle": mockup.get("product_angle", "спереди"),
                        "created_time": time.time()
                    }
                }
                
                # Google Drive отключен
                
                # Загружаем на сервер если включено
                from services.upload_services import upload_to_server
                upload_to_server(mockup["image_data"], gallery_entry["metadata"], mockup.get("description", ""))
                
                # Загружаем на FTP если включено
                from services.upload_services import upload_to_ftp
                upload_to_ftp(mockup["image_data"], gallery_entry["metadata"], mockup.get("description", ""))

def display_mockups_dynamically(mockups: dict, result: dict):
    """Динамическое отображение мокапов с возможностью обновления"""
    
    # Проверяем, что mockups не пустой
    if not mockups:
        st.error("❌ Критическая ошибка: 'mockups'")
        st.info("Попробуйте перезагрузить страницу или проверить изображения")
        
        # Кнопка для сброса session_state
        if st.button("🔄 Сбросить состояние", help="Очистить все данные и начать заново"):
            # Очищаем все ключи связанные с мокапами
            keys_to_clear = [
                'last_result', 'mockup_containers', 'generated_mockups',
                'gallery_cache', 'regenerate_params', 'batch_results'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return
    
    # Проверка, использовался ли fallback
    fallback_used = mockups.get("fallback_used", False)
    
    # Создаем контейнеры для динамического обновления
    if "mockup_containers" not in st.session_state:
        st.session_state.mockup_containers = {}
    
    # Gemini мокапы (если есть)
    if "gemini_mockups" in mockups:
        gemini_mockups = mockups["gemini_mockups"]
        
        if gemini_mockups:
            for i, mockup in enumerate(gemini_mockups):
                # Создаем уникальный ключ для контейнера
                container_key = f"mockup_{i}"
                
                # Создаем контейнер если его нет
                if container_key not in st.session_state.mockup_containers:
                    st.session_state.mockup_containers[container_key] = st.empty()
                
                # Получаем контейнер
                mockup_container = st.session_state.mockup_containers[container_key]
                
                # Отображаем мокап в контейнере
                with mockup_container.container():
                    if "description" in mockup:
                        st.write(f"**Вариант {i+1}:** {mockup['description']}")
                    
                    # Если есть изображение от Gemini
                    if "image_data" in mockup:
                        try:
                            # image_data уже является bytes от Gemini
                            image_data = mockup["image_data"]
                            image = Image.open(io.BytesIO(image_data))
                            
                            # Конвертируем в RGB для совместимости с JPEG
                            if image.mode in ('RGBA', 'LA', 'P'):
                                processor = ImageProcessor()
                                image = processor.convert_to_rgb(image)
                                # Обновляем image_data
                                img_byte_arr = io.BytesIO()
                                image.save(img_byte_arr, format='JPEG', quality=95)
                                image_data = img_byte_arr.getvalue()
                            
                            # Отображаем изображение
                            st.image(image_data, use_column_width=True)
                            
                            # Кнопки действий
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Кнопка скачивания
                                st.download_button(
                                    label="Скачать",
                                    data=image_data,
                                    file_name=f"mockup_{i+1}.jpg",
                                    mime="image/jpeg",
                                    use_container_width=True
                                )
                            
                            with col2:
                                # Кнопка перегенерации
                                if st.button(f"Перегенерировать мокап {i+1}", use_container_width=True):
                                    # Сохраняем параметры для перегенерации
                                    st.session_state.regenerate_params = {
                                        "mockup_index": i,
                                        "original_mockup": mockup,
                                        "original_result": result,
                                        "container_key": container_key
                                    }
                                    st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Ошибка отображения изображения: {e}")
                            st.error("Попробуйте перезагрузить страницу")
    
    # Fallback мокапы (если есть)
    if "fallback_mockups" in mockups and mockups["fallback_mockups"]:
        st.warning("⚠️ Использованы локальные мокапы (Gemini недоступен)")
        
        for i, mockup in enumerate(mockups["fallback_mockups"]):
            if "image_path" in mockup:
                try:
                    with open(mockup["image_path"], "rb") as f:
                        image_data = f.read()
                    
                    st.image(image_data, use_column_width=True)
                    
                    # Кнопка скачивания для fallback
                    st.download_button(
                        label=f"Скачать локальный мокап {i+1}",
                        data=image_data,
                        file_name=f"fallback_mockup_{i+1}.jpg",
                        mime="image/jpeg"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Ошибка загрузки локального мокапа: {e}")

def regenerate_mockup_dynamically(mockup_index: int, original_mockup: dict, original_result: dict, container_key: str):
    """Динамическое пересоздание мокапа с обновлением в реальном времени"""
    
    # Получаем контейнер для обновления
    mockup_container = st.session_state.mockup_containers[container_key]
    
    # Показываем индикатор загрузки
    with mockup_container.container():
        st.info(f"🔄 Пересоздание мокапа {mockup_index + 1}...")
        
        # Создаем прогресс-бар
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Обновляем статус
            status_text.text("🔄 Подключение к Gemini...")
            progress_bar.progress(20)
            time.sleep(0.5)
            
            # Получаем генератор
            from mockup_generator import MockupGenerator
            generator = MockupGenerator()
            
            # Извлекаем параметры из оригинального результата
            mockup_style = original_result.get("style", "modern")
            logo_application = original_result.get("logo_application", "embroidery")
            custom_prompt = original_result.get("custom_prompt", "")
            product_color = original_result.get("product_color", "белый")
            product_angle = original_result.get("product_angle", "спереди")
            logo_position = original_result.get("logo_position", "центр")
            logo_size = original_result.get("logo_size", "средний")
            logo_color = original_result.get("logo_color", "как на фото")
            
            # Обновляем статус
            status_text.text("🎨 Генерация нового мокапа...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            # Генерируем новый мокап с теми же параметрами
            new_result = generator.generate_mockup(
                st.session_state.product_image, st.session_state.logo_image,
                mockup_style, logo_application, custom_prompt, product_color,
                product_angle, logo_position, logo_size, logo_color
            )
            
            # Обновляем статус
            status_text.text("✅ Обработка результата...")
            progress_bar.progress(80)
            time.sleep(0.5)
            
            if new_result and "mockups" in new_result and new_result["mockups"]:
                # Обновляем отображение
                update_mockup_display(mockup_index, new_result["mockups"][0], new_result, container_key)
                
                # Обновляем статус
                status_text.text("✅ Мокап успешно пересоздан!")
                progress_bar.progress(100)
                time.sleep(1)
                
                # Очищаем индикаторы
                status_text.empty()
                progress_bar.empty()
                
            else:
                st.error("❌ Ошибка пересоздания мокапа")
                st.error("Попробуйте еще раз или перезагрузите страницу")
                
        except Exception as e:
            st.error(f"❌ Критическая ошибка при пересоздании: {e}")
            st.error("Попробуйте перезагрузить страницу")

def update_mockup_display(mockup_index: int, new_mockup: dict, result: dict, container_key: str):
    """Обновление отображения мокапа после перегенерации"""
    
    # Получаем контейнер
    mockup_container = st.session_state.mockup_containers[container_key]
    
    # Обновляем отображение
    with mockup_container.container():
        if "description" in new_mockup:
            st.write(f"**Вариант {mockup_index + 1}:** {new_mockup['description']}")
        
        # Если есть изображение
        if "image_data" in new_mockup:
            try:
                # image_data уже является bytes от Gemini
                image_data = new_mockup["image_data"]
                image = Image.open(io.BytesIO(image_data))
                
                # Конвертируем в RGB для совместимости с JPEG
                if image.mode in ('RGBA', 'LA', 'P'):
                    processor = ImageProcessor()
                    image = processor.convert_to_rgb(image)
                    # Обновляем image_data
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG', quality=95)
                    image_data = img_byte_arr.getvalue()
                
                # Отображаем изображение
                st.image(image_data, use_column_width=True)
                
                # Кнопки действий
                col1, col2 = st.columns(2)
                
                with col1:
                    # Кнопка скачивания
                    st.download_button(
                        label="Скачать",
                        data=image_data,
                        file_name=f"mockup_{mockup_index + 1}.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
                
                with col2:
                    # Кнопка перегенерации
                    if st.button(f"Перегенерировать мокап {mockup_index + 1}", use_container_width=True):
                        # Сохраняем параметры для перегенерации
                        st.session_state.regenerate_params = {
                            "mockup_index": mockup_index,
                            "original_mockup": new_mockup,
                            "original_result": result,
                            "container_key": container_key
                        }
                        
                        # Запускаем перегенерацию
                        regenerate_mockup_dynamically(mockup_index, new_mockup, result, container_key)
                
            except Exception as e:
                st.error(f"❌ Ошибка отображения изображения: {e}")
                st.error("Попробуйте перезагрузить страницу")
