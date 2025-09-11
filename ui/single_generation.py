"""
Модуль для интерфейса одиночной генерации мокапов
"""

import streamlit as st
import time
from PIL import Image
from image_processor import ImageProcessor

def single_generation_interface():
    """Интерфейс одиночной генерации мокапов"""
    
    st.subheader("🎨 Генерация мокапа")
    
    # Проверяем наличие изображений
    if "product_image" in st.session_state and "logo_image" in st.session_state:
        
        # Показываем загруженные изображения
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Товар:**")
            st.image(st.session_state.product_image, width=200)
        
        with col2:
            st.write("**🏷️ Логотип:**")
            st.image(st.session_state.logo_image, width=200)
        
        # Настройки генерации
        with st.expander("⚙️ Настройки генерации", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                mockup_style = st.selectbox(
                    "Стиль мокапа",
                    ["modern", "vintage", "minimalist", "luxury", "casual", "sporty"],
                    index=0,
                    help="Выберите стиль для генерации мокапа"
                )
                
                product_color = st.selectbox(
                    "Цвет товара",
                    ["белый", "черный", "серый", "синий", "красный", "зеленый", "как на фото"],
                    index=6,
                    help="Выберите цвет товара"
                )
                
                product_angle = st.selectbox(
                    "Ракурс",
                    ["спереди", "сбоку", "сзади", "сверху", "3/4"],
                    index=0,
                    help="Выберите ракурс для показа товара"
                )
            
            with col2:
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
            
            custom_prompt = st.text_area(
                "Дополнительные требования",
                placeholder="Опишите дополнительные требования к мокапу...",
                help="Дополнительные пожелания к генерации мокапа"
            )
            
            # Дополнительные опции
            col1, col2, col3 = st.columns(3)
            with col1:
                add_tag = st.checkbox("Добавить бирку", help="Добавить бирку с информацией о товаре")
            with col2:
                add_person = st.checkbox("Показать в использовании", help="Показать товар на человеке")
            with col3:
                add_badge = st.checkbox("Добавить шильдик", help="Добавить металлический шильдик")
        
        # Паттерн (опционально)
        if "pattern_image" in st.session_state:
            st.write("**🎨 Паттерн:**")
            st.image(st.session_state.pattern_image, width=100)
        
        # Кнопка генерации
        if st.button("Сгенерировать мокап", type="primary", use_container_width=True):
            # Получаем генератор
            from main import get_mockup_generator
            generator = get_mockup_generator()
            
            # Создаем расширенный промпт
            extended_prompt = custom_prompt.strip()
            
            # Добавляем дополнительные требования
            if add_tag:
                extended_prompt += " Добавить бирку с информацией о товаре."
            if add_person:
                extended_prompt += " Показать товар в использовании на человеке."
            if add_badge:
                extended_prompt += " Добавить металлический шильдик с логотипом на товар."
            
            # Автоматически определяем использование паттерна по загруженному изображению
            if "pattern_image" in st.session_state:
                extended_prompt += " Создать повторяющийся паттерн с загруженным паттерном по всей поверхности товара."
            
            # Показываем настройки генерации в схлопывающемся блоке
            with st.expander("⚙️ Настройки генерации"):
                st.info(f"📦 Товар: {mockup_style} стиль, {product_color} цвет, {product_angle} ракурс")
                st.info(f"🏷️ Логотип: {logo_application}, {logo_position}, {logo_size} размер, {logo_color} цвет")
            
            # Показываем дополнительные опции
            additional_options = []
            if add_tag:
                additional_options.append("бирка")
            if add_person:
                additional_options.append("в использовании")
            if add_badge:
                additional_options.append("шильдик")
            if "pattern_image" in st.session_state:
                additional_options.append("паттерн")
            
            if additional_options:
                st.info(f"🔧 Дополнительно: {', '.join(additional_options)}")
            
            if custom_prompt.strip():
                st.info(f"📝 Дополнительные требования: {custom_prompt}")
            
            # Показываем только статус генерации
            st.info("🚀 Генерируем мокап с помощью AI...")
            
            # Получаем изображения из сессии
            product_image = st.session_state.product_image
            logo_image = st.session_state.logo_image
            pattern_image = st.session_state.get("pattern_image", None)
            
            # Генерация мокапов
            try:
                result = generator.generate_mockups(
                    product_image=product_image,
                    logo_image=logo_image,
                    style=mockup_style,
                    logo_application=logo_application,
                    custom_prompt=extended_prompt,
                    product_color=product_color,
                    product_angle=product_angle,
                    logo_position=logo_position,
                    logo_size=logo_size,
                    logo_color=logo_color,
                    pattern_image=pattern_image
                )
                
                if result["status"] == "success":
                    st.success(f"✅ Мокапы сгенерированы за {result['processing_time']:.2f} секунд")
                    
                    # Показываем текстовый ответ от Gemini, если есть
                    if "mockups" in result and result["mockups"]:
                        for i, mockup in enumerate(result["mockups"]):
                            if "text_response" in mockup and mockup["text_response"]:
                                with st.expander(f"📝 Текстовый ответ от Gemini (мокап {i+1})"):
                                    st.write(mockup["text_response"])
                    
                    # Отображение результатов
                    from ui.display_results import display_results
                    display_results(result)
                    
                elif result["status"] == "partial_success":
                    st.warning("⚠️ Частичный успех - использованы локальные мокапы")
                    from ui.display_results import display_results
                    display_results(result)
                    
                else:
                    st.error("❌ Ошибка генерации мокапов")
                    if "text_response" in result:
                        with st.expander("📝 Текстовый ответ от Gemini"):
                            st.write(result["text_response"])
                    st.error(result.get("error", "Неизвестная ошибка"))
                    
                    # Показываем fallback мокапы даже при ошибке
                    if "mockups" in result:
                        from ui.display_results import display_results
                        display_results(result)
                
            except Exception as e:
                st.error(f"❌ Критическая ошибка: {e}")
                st.error("Попробуйте перезагрузить страницу или проверить изображения")
    
    else:
        st.info("👆 Загрузите изображение товара и логотип для начала генерации")
    
