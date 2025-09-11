"""
Модуль для интерфейса пакетной обработки мокапов
"""

import streamlit as st
import time
from PIL import Image
from image_processor import ImageProcessor

def batch_processing_interface():
    """Интерфейс пакетной обработки мокапов"""
    
    st.subheader("📦 Пакетная обработка")
    
    # Проверяем наличие изображений
    if "batch_product_images" in st.session_state and "batch_logo_image" in st.session_state:
        
        # Показываем загруженные изображения
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**📦 Товары для коллекции:**")
            if st.session_state.batch_product_images:
                # Показываем сетку товаров
                cols = st.columns(2)
                for i, img in enumerate(st.session_state.batch_product_images):
                    with cols[i % 2]:
                        st.image(img, width=60)
                        st.caption(f"Товар {i+1}")
        
        with col2:
            st.write("**🏷️ Логотип для коллекции:**")
            st.image(st.session_state.batch_logo_image, width=80)
        
        with col3:
            st.write("**🔧 Дополнительно:**")
            
            # Паттерн (опционально)
            if "batch_pattern_image" in st.session_state:
                st.write("**Паттерн:**")
                st.image(st.session_state.batch_pattern_image, width=60)
            
            # Настройки коллекции
            collection_style = st.selectbox(
                "Стиль коллекции",
                ["modern", "vintage", "minimalist", "luxury", "casual", "sporty"],
                index=0,
                help="Выберите стиль для всей коллекции"
            )
            
            product_color = st.selectbox(
                "Цвет товаров",
                ["белый", "черный", "серый", "синий", "красный", "зеленый", "как на фото"],
                index=6,
                help="Выберите цвет для всех товаров"
            )
            
            logo_application = st.selectbox(
                "Тип нанесения логотипа",
                ["вышивка", "печать", "аппликация", "вышивка+печать", "как на фото"],
                index=0,
                help="Выберите способ нанесения логотипа"
            )
            
            logo_position = st.selectbox(
                "Расположение логотипа",
                ["центр", "левый верх", "правый верх", "левый низ", "правый низ", "как на фото"],
                index=0,
                help="Выберите расположение логотипа"
            )
            
            logo_size = st.selectbox(
                "Размер логотипа",
                ["очень маленький", "маленький", "средний", "большой", "очень большой", "как на фото"],
                index=0,
                help="Выберите размер логотипа"
            )
            
            logo_color = st.selectbox(
                "Цвет логотипа",
                ["как на фото", "белый", "черный", "цветной", "монохромный"],
                index=0,
                help="Выберите цвет логотипа"
            )
            
            # Дополнительные опции
            add_tag = st.checkbox("Добавить бирку", help="Добавить бирку с информацией о товаре")
            add_person = st.checkbox("Показать в использовании", help="Показать товар на человеке")
            add_badge = st.checkbox("Добавить шильдик", help="Добавить металлический шильдик")
        
        # Кнопка генерации
        if st.button("Сгенерировать мокапы", type="primary", use_container_width=True):
            # Получаем процессор пакетной обработки
            from batch_processor import BatchProcessor
            batch_processor = BatchProcessor()
            
            # Создаем настройки коллекции
            collection_settings = {
                "product_color": product_color,
                "collection_style": collection_style,
            }
            
            # Создаем настройки логотипа
            logo_settings = {
                "application": logo_application,
                "position": logo_position,
                "size": logo_size,
                "color": logo_color
            }
            
            # Создаем дополнительные опции
            additional_options = {
                "add_tag": add_tag,
                "add_person": add_person,
                "add_badge": add_badge
            }
            
            # Получаем паттерн если есть
            pattern_image = st.session_state.get("batch_pattern_image", None)
            
            # Показываем статус
            with st.spinner("🔄 Анализ коллекции и генерация мокапов..."):
                try:
                    # Анализируем коллекцию
                    analysis_result = batch_processor.analyze_collection(
                        st.session_state.batch_product_images,
                        st.session_state.batch_logo_image,
                        collection_settings,
                        logo_settings,
                        additional_options,
                        pattern_image
                    )
                    
                    if analysis_result["status"] == "success":
                        st.success("✅ Коллекция проанализирована успешно")
                        
                        # Показываем результаты анализа
                        with st.expander("📊 Результаты анализа коллекции"):
                            st.write(f"**Количество товаров:** {len(analysis_result['individual_prompts'])}")
                            st.write(f"**Стиль коллекции:** {analysis_result['collection_style']}")
                            st.write(f"**Тип нанесения:** {analysis_result['logo_application']}")
                            
                            # Показываем созданные промпты
                            with st.expander("📝 Созданные промпты для товаров"):
                                for i, prompt_data in enumerate(analysis_result["individual_prompts"]):
                                    st.write(f"**Товар {i+1}:**")
                                    st.write(f"- Стиль: {prompt_data.get('style', collection_style)}")
                                    st.write(f"- Нанесение: {prompt_data.get('logo_application', 'embroidery')}")
                                    st.write(f"- Расположение: {prompt_data.get('logo_position', 'центр')}")
                                    st.write(f"- Размер: {prompt_data.get('logo_size', 'средний')}")
                                    if prompt_data.get('reasoning'):
                                        st.write(f"- Обоснование: {prompt_data['reasoning']}")
                        
                        # Генерируем мокапы
                        batch_result = batch_processor.process_batch(
                            st.session_state.batch_product_images,
                            st.session_state.batch_logo_image,
                            analysis_result["individual_prompts"],
                            logo_settings,
                            additional_options,
                            pattern_image
                        )
                        
                        if batch_result["status"] == "success":
                            st.success(f"✅ Пакетная обработка завершена за {batch_result['processing_time']:.2f} секунд")
                            
                            # Сохраняем результат
                            st.session_state.batch_results = batch_result
                            
                            # Отображаем результаты
                            display_batch_results(batch_result)
                            
                        else:
                            st.error("❌ Ошибка пакетной обработки")
                            st.error(batch_result.get("error", "Неизвестная ошибка"))
                    
                    else:
                        st.error("❌ Ошибка анализа коллекции")
                        st.error(analysis_result.get("error", "Неизвестная ошибка"))
                
                except Exception as e:
                    st.error(f"❌ Критическая ошибка: {e}")
                    st.error("Попробуйте перезагрузить страницу или проверить изображения")
    
    else:
        st.info("👆 Загрузите изображения товаров и логотип для начала пакетной обработки")

def display_batch_results(batch_result: dict):
    """Отображение результатов пакетной обработки"""
    
    if "results" not in batch_result:
        st.error("❌ Нет результатов для отображения")
        return
    
    results = batch_result["results"]
    
    st.subheader("📊 Результаты пакетной обработки")
    
    # Показываем статистику
    st.info(f"📈 Обработано товаров: {len(results)}")
    
    # Отображаем результаты по товарам
    for i, result in enumerate(results):
        with st.expander(f"Товар {i+1}", expanded=True):
            if result["status"] == "success":
                st.success(f"✅ Товар {i+1} обработан успешно")
                
                # Показываем мокапы
                if "mockups" in result and result["mockups"]:
                    for j, mockup in enumerate(result["mockups"]):
                        if "image_data" in mockup:
                            st.image(mockup["image_data"], use_column_width=True)
                            
                            # Кнопка скачивания
                            st.download_button(
                                label=f"Скачать мокап {j+1}",
                                data=mockup["image_data"],
                                file_name=f"batch_mockup_{i+1}_{j+1}.jpg",
                                mime="image/jpeg"
                            )
                
                # Показываем информацию о товаре
                if "prompt_data" in result:
                    prompt_data = result["prompt_data"]
                    st.write(f"**Стиль:** {prompt_data.get('style', 'Неизвестно')}")
                    st.write(f"**Нанесение:** {prompt_data.get('logo_application', 'Неизвестно')}")
                    st.write(f"**Расположение:** {prompt_data.get('logo_position', 'Неизвестно')}")
                    st.write(f"**Размер:** {prompt_data.get('logo_size', 'Неизвестно')}")
            
            else:
                st.error(f"❌ Ошибка обработки товара {i+1}")
                st.error(result.get("error", "Неизвестная ошибка"))
    
    # Кнопка очистки результатов
    if st.button("Очистить результаты", type="secondary"):
        if "batch_results" in st.session_state:
            del st.session_state.batch_results
        st.rerun()
