"""
Веб-интерфейс для AI Mockup Generator
Использует Streamlit для простого и быстрого интерфейса
"""
import streamlit as st
import os
import json
from datetime import datetime, timedelta
from PIL import Image
import time
from typing import Optional

# Импортируем конфигурацию после инициализации Streamlit
from config import get_config, STREAMLIT_PORT, STREAMLIT_HOST, SERVER_STORAGE_ENABLED, FTP_ENABLED
from auth import is_authenticated, login_form, logout_button, require_auth, get_user_info
from mockup_generator import MockupGenerator
from batch_processor import BatchProcessor

# Получаем актуальную конфигурацию
config = get_config()

# Настройка страницы
st.set_page_config(
    page_title="AI Mockup Generator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Кастомные CSS стили для компактности и фоновых блоков
st.markdown("""
<style>
    /* Компактные заголовки */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Уменьшаем отступы между элементами */
    .stSelectbox > div > div {
        margin-bottom: 0.5rem;
    }
    
    /* Компактные кнопки */
    .stButton > button {
        height: 2.5rem;
        font-size: 0.9rem;
    }
    
    /* Компактные превью изображений */
    .stImage > img {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Уменьшаем размеры текстовых областей */
    .stTextArea > div > div > textarea {
        font-size: 0.9rem;
    }
    
    /* Дополнительные стили для контейнеров блоков */
    .stContainer {
        background: #f8f9fa !important;
        padding: 1.5rem !important;
        border-radius: 0.5rem !important;
        margin: 1rem 0 !important;
        border: 1px solid #e9ecef !important;
    }
    
    /* Стили для заголовков в контейнерах */
    .stContainer h3 {
        color: #495057 !important;
        margin-bottom: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* Увеличиваем расстояния между элементами */
    .stContainer .stSelectbox,
    .stContainer .stTextInput,
    .stContainer .stTextArea,
    .stContainer .stCheckbox,
    .stContainer .stFileUploader {
        margin-bottom: 1rem !important;
    }
    
    /* Дополнительные отступы для разделителей */
    .stContainer hr {
        margin: 1.5rem 0 !important;
    }
    
    /* Увеличиваем расстояния между колонками */
    .stColumn {
        padding: 0 0.5rem !important;
    }
    
    /* Дополнительные отступы для основного контейнера */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    
    /* Кнопки режима */
    .stButton > button[kind="primary"] {
        background-color: #6c757d !important;
        color: white !important;
        border: 1px solid #6c757d !important;
        font-weight: 600 !important;
        border-radius: 0.5rem !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #f8f9fa !important;
        color: #6c757d !important;
        border: 1px solid #e9ecef !important;
        font-weight: 500 !important;
        border-radius: 0.5rem !important;
    }
    
    .stButton > button:hover {
        background-color: #5a6268 !important;
        color: white !important;
        border-color: #5a6268 !important;
        transform: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация генераторов
@st.cache_resource
def get_mockup_generator():
    return MockupGenerator()

@st.cache_resource
def get_batch_processor():
    return BatchProcessor()

# Очистка кэша для обновления BatchProcessor
def clear_batch_processor_cache():
    get_batch_processor.clear()

def main():
    """Основная функция веб-интерфейса"""
    
    # Проверка аутентификации
    if not is_authenticated():
        login_form()
        return
    
    # Обработка перегенерации
    if "regenerate_params" in st.session_state:
        regenerate_params = st.session_state.regenerate_params
        regenerate_mockup_dynamically(
            regenerate_params["mockup_index"],
            regenerate_params["original_mockup"],
            regenerate_params["original_result"],
            regenerate_params["container_key"]
        )
        # Очищаем параметры после обработки
        del st.session_state.regenerate_params
        # Принудительно обновляем страницу
        st.rerun()
        return
    
    # Главная страница генерации мокапов
    
    # Основной заголовок
    st.markdown("### Headcorn Mockup")
    
    # Информация о пользователе и кнопка выхода в правом верхнем углу
    col1, col2 = st.columns([4, 1])
    with col1:
        # Показываем информацию о пользователе
        if is_authenticated():
            user_info = get_user_info()
            if user_info:
                st.caption(f"👤 {user_info['name']} ({user_info['email']})")
    with col2:
        logout_button()
    
    # Выбор режима работы с улучшенным дизайном
    st.markdown("---")
    st.markdown("### Режим работы")
    
    # Создаем кнопки-переключатели
    col1, col2, col3 = st.columns(3)
    
    with col1:
        single_type = "primary" if st.session_state.get('mode', 'single') == 'single' else "secondary"
        if st.button("Одиночная генерация", key="single_mode", use_container_width=True, type=single_type):
            st.session_state.mode = 'single'
            st.rerun()
    
    with col2:
        batch_type = "primary" if st.session_state.get('mode', 'single') == 'batch' else "secondary"
        if st.button("Пакетная обработка", key="batch_mode", use_container_width=True, type=batch_type):
            st.session_state.mode = 'batch'
            st.rerun()
    
    with col3:
        creative_type = "primary" if st.session_state.get('mode', 'single') == 'creative' else "secondary"
        if st.button("Креативный генератор", key="creative_mode", use_container_width=True, type=creative_type):
            st.session_state.mode = 'creative'
            st.rerun()
    
    # Определяем режим
    mode = st.session_state.get('mode', 'single')
    
    # Показываем соответствующий интерфейс
    if mode == 'single':
        single_generation_interface()
    elif mode == 'batch':
        batch_processing_interface()
    else:
        creative_generation_interface()

def single_generation_interface():
    """Интерфейс для одиночной генерации мокапов"""
    
    # Обработка пересоздания
    if "regenerate_params" in st.session_state:
        regenerate_params = st.session_state.regenerate_params
        mockup_index = regenerate_params["mockup_index"]
        
        st.info(f"🔄 Пересоздание мокапа {mockup_index + 1}...")
        
        with st.spinner("Пересоздание мокапа с теми же параметрами..."):
            try:
                generator = get_mockup_generator()
                
                # Получаем параметры из оригинального результата
                original_result = regenerate_params["original_result"]
                
                # Извлекаем параметры из оригинального результата
                mockup_style = original_result.get("mockup_style", "modern")
                logo_application = original_result.get("logo_application", "embroidery")
                custom_prompt = original_result.get("custom_prompt", "")
                product_color = original_result.get("product_color", "как на фото")
                product_angle = original_result.get("product_angle", "спереди")
                logo_position = original_result.get("logo_position", "центр")
                logo_size = original_result.get("logo_size", "средний")
                logo_color = original_result.get("logo_color", "как на фото")
                
                # Генерируем новый мокап с теми же параметрами
                new_result = generator.generate_mockup(
                    st.session_state.product_image, st.session_state.logo_image,
                    mockup_style, logo_application, custom_prompt, product_color,
                    product_angle, logo_position, logo_size, logo_color
                )
                
                # Заменяем только выбранный мокап в оригинальном результате
                if new_result and "mockups" in new_result and "gemini_mockups" in new_result["mockups"]:
                    new_mockups = new_result["mockups"]["gemini_mockups"]
                    if new_mockups and len(new_mockups) > 0:
                        # Заменяем конкретный мокап
                        original_result["mockups"]["gemini_mockups"][mockup_index] = new_mockups[0]
                        # Сохраняем обновленный результат в session_state
                        st.session_state.last_result = original_result
                        st.success(f"✅ Мокап {mockup_index + 1} пересоздан!")
                
                # Очищаем параметры пересоздания
                del st.session_state.regenerate_params
                
            except Exception as e:
                st.error(f"❌ Ошибка пересоздания: {e}")
                del st.session_state.regenerate_params
        
        # Показываем обновленные результаты
        if "last_result" in st.session_state:
            display_results(st.session_state.last_result)
        return
    
    # Разделяем настройки на логические блоки в колонках с фоновым разделением
    with st.expander("⚙️ Настройки", expanded=True):
        col1, col2, col3 = st.columns(3)
    
    with col1:
        # Блок "Товар" с красивым фоном
        with st.container():
            st.markdown("### Товар")
            
            # Загрузка изображения товара
            product_file = st.file_uploader(
                "Загрузите товар",
                type=['jpg', 'jpeg', 'png', 'webp'],
                key="product"
            )
            
            if product_file:
                product_image = Image.open(product_file)
                # Конвертируем в RGB для совместимости с JPEG
                if product_image.mode in ('RGBA', 'LA', 'P'):
                    from image_processor import ImageProcessor
                    processor = ImageProcessor()
                    product_image = processor.convert_to_rgb(product_image)
                st.session_state.product_image = product_image
                preview_size = (120, 120)
                preview_image = product_image.copy()
                preview_image.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_image, caption="Товар", width=120)
                st.caption(f"{product_image.size[0]}x{product_image.size[1]}")
            elif "product_image" in st.session_state:
                product_image = st.session_state.product_image
                preview_size = (120, 120)
                preview_image = product_image.copy()
                preview_image.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_image, caption="Товар", width=120)
                st.caption(f"{product_image.size[0]}x{product_image.size[1]}")
            
            st.markdown("---")
            
            # Настройки товара
            mockup_style = st.selectbox(
                "Стиль",
                ["Современный", "Премиальный", "Минималистичный", "В динамике"],
                help="Стиль мокапа"
            )
            
            product_color = st.text_input(
                "Цвет товара",
                value="как на фото",
                help="Цвет товара"
            )
            
            product_angle = st.selectbox(
                "Ракурс",
                ["как на фото", "спереди", "в полуоборот", "сверху", "в интерьере", "сбоку", "под углом"],
                help="Угол съемки"
            )
    
    with col2:
        # Блок "Логотип" с красивым фоном
        with st.container():
            st.markdown("### Логотип")
            
            # Загрузка логотипа
            logo_file = st.file_uploader(
                "Загрузите логотип",
                type=['jpg', 'jpeg', 'png', 'webp'],
                key="logo"
            )
            
            if logo_file:
                logo_image = Image.open(logo_file)
                # Конвертируем в RGB для совместимости с JPEG
                if logo_image.mode in ('RGBA', 'LA', 'P'):
                    from image_processor import ImageProcessor
                    processor = ImageProcessor()
                    logo_image = processor.convert_to_rgb(logo_image)
                st.session_state.logo_image = logo_image
                preview_size = (120, 120)
                preview_logo = logo_image.copy()
                preview_logo.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_logo, caption="Логотип", width=120)
                st.caption(f"{logo_image.size[0]}x{logo_image.size[1]}")
            elif "logo_image" in st.session_state:
                logo_image = st.session_state.logo_image
                preview_size = (120, 120)
                preview_logo = logo_image.copy()
                preview_logo.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_logo, caption="Логотип", width=120)
                st.caption(f"{logo_image.size[0]}x{logo_image.size[1]}")
            
            st.markdown("---")
            
            # Настройки логотипа
            logo_application_options = ["вышивка", "печать", "ткачество", "тиснение", "сублимация", "силикон", "термоперенос", "шелкография", "цифровая печать", "лазерная гравировка", "патч"]
            logo_application = st.selectbox(
                "Тип нанесения",
                logo_application_options,
                help="Тип нанесения логотипа"
            )
            
            custom_application = st.text_input(
                "Или введите свой тип нанесения",
                placeholder="Например: аппликация, гравировка",
                help="Введите свой тип нанесения, если его нет в списке"
            )
            
            if custom_application.strip():
                logo_application = custom_application.strip()
                logo_application_from_select = None
            else:
                logo_application_from_select = logo_application
            
            logo_position = st.selectbox(
                "Расположение",
                ["центр", "верхний левый угол", "верхний правый угол", "нижний левый угол", "нижний правый угол", "левый бок", "правый бок", "верх", "низ"],
                help="Расположение логотипа"
            )
            
            logo_size = st.selectbox(
                "Размер",
                ["очень маленький", "маленький", "средний", "большой", "очень большой"],
                help="Размер логотипа"
            )
            
            logo_color = st.selectbox(
                "Цвет",
                ["как на фото", "черный", "белый"],
                help="Цвет логотипа"
            )
    
    with col3:
        # Блок "Дополнительно" с красивым фоном
        with st.container():
            st.markdown("### Дополнительно")
            
            # Загрузка паттерна
            pattern_file = st.file_uploader(
                "Паттерн (опционально)",
                type=['jpg', 'jpeg', 'png', 'webp'],
                key="pattern",
                help="Паттерн для нанесения на товар"
            )
            
            if pattern_file:
                pattern_image = Image.open(pattern_file)
                # Конвертируем в RGB для совместимости с JPEG
                if pattern_image.mode in ('RGBA', 'LA', 'P'):
                    from image_processor import ImageProcessor
                    processor = ImageProcessor()
                    pattern_image = processor.convert_to_rgb(pattern_image)
                st.session_state.pattern_image = pattern_image
                preview_size = (120, 120)
                preview_pattern = pattern_image.copy()
                preview_pattern.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_pattern, caption="Паттерн", width=120)
                st.caption(f"{pattern_image.size[0]}x{pattern_image.size[1]}")
            elif "pattern_image" in st.session_state:
                pattern_image = st.session_state.pattern_image
                preview_size = (120, 120)
                preview_pattern = pattern_image.copy()
                preview_pattern.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_pattern, caption="Паттерн", width=120)
                st.caption(f"{pattern_image.size[0]}x{pattern_image.size[1]}")
            
            st.markdown("---")
            
            # Дополнительные настройки
            add_tag = st.checkbox("Добавить бирку", value=False, help="Добавить этикетку или бирку с логотипом к товару")
            add_person = st.checkbox("Добавить человека", value=False, help="Показать товар в использовании человеком")
            
            st.markdown("**Доп. нанесение**")
            add_badge = st.checkbox("Добавить шильдик", value=False, help="Добавить металлический шильдик с логотипом")
            
            st.markdown("**Детали**")
            custom_prompt = st.text_area(
                "Особые требования",
                placeholder="Например: 'логотип в правом углу', 'добавить тени'",
                height=60,
                help="Дополнительные детали для промпта"
            )
    
    # Компактные кнопки управления
    if ("product_image" in st.session_state and "logo_image" in st.session_state):
        st.markdown("---")
        
        # Компактные кнопки управления
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("Сгенерировать мокап", type="primary", use_container_width=True):
                with st.spinner("Генерация мокапов..."):
                    try:
                        generator = get_mockup_generator()
                        
                        # Словарь перевода русских названий в английские ключи
                        logo_application_translation = {
                            "вышивка": "embroidery",
                            "печать": "printing", 
                            "ткачество": "woven",
                            "тиснение": "embossed",
                            "сублимация": "sublimation",
                            "силикон": "silicone",
                            "термоперенос": "heat_transfer",
                            "шелкография": "screen_print",
                            "цифровая печать": "digital_print",
                            "лазерная гравировка": "laser_engraving",
                            "патч": "patch"
                        }
                        
                        # Словарь перевода стилей
                        style_translation = {
                            "Современный": "modern",
                            "Премиальный": "luxury",
                            "Минималистичный": "minimal",
                            "В динамике": "dynamic"
                        }
                        
                        # Переводим русское название в английский ключ
                        # Если используется кастомное значение, используем его как есть
                        if custom_application.strip():
                            logo_application_key = custom_application.strip()  # Кастомное значение остается как есть
                        else:
                            logo_application_key = logo_application_translation.get(logo_application, "embroidery")
                        mockup_style_key = style_translation.get(mockup_style, "modern")
                        
                        
                        # Формируем расширенный промпт с дополнительными опциями
                        extended_prompt = custom_prompt
                        
                        # Добавляем логику для удаления фоновых объектов при смене ракурса
                        if product_angle != "как на фото":
                            extended_prompt += " Удалить все фоновые объекты, людей, мебель и окружение. Оставить только основной товар/товары на чистом фоне."
                        
                        if add_tag:
                            extended_prompt += " Добавить этикетку или бирку с логотипом к товару. Этикетка должна содержать логотип, который был загружен пользователем."
                        if add_person:
                            extended_prompt += " Показать товар в использовании человеком, человек должен держать или использовать товар."
                        if add_badge:
                            extended_prompt += " Добавить металлический шильдик с логотипом на товар."
                        # Автоматически определяем использование паттерна по загруженному изображению
                        if "pattern_image" in st.session_state:
                            extended_prompt += " Создать повторяющийся паттерн с загруженным паттерном по всей поверхности товара."
                        
                        
                        # Показываем дополнительные опции
                        additional_options = []
                        if add_tag:
                            additional_options.append("бирка")
                        if add_person:
                            additional_options.append("человек")
                        if add_badge:
                            additional_options.append("шильдик")
                        # Автоматически добавляем паттерн если загружен
                        if "pattern_image" in st.session_state:
                            additional_options.append("паттерн")
                        
                        if additional_options:
                            st.info(f"Дополнительно: {', '.join(additional_options)}")
                        
                        if custom_prompt.strip():
                            st.info(f"Дополнительные требования: {custom_prompt}")
                        
                        # Показываем только статус генерации
                        st.info("Генерируем мокап с помощью AI...")
                        
                        
                        # Получаем изображения из сессии
                        product_image = st.session_state.product_image
                        logo_image = st.session_state.logo_image
                        pattern_image = st.session_state.get("pattern_image", None)
                        
                        # Генерация мокапов
                        result = generator.generate_mockups(
                            product_image=product_image,
                            logo_image=logo_image,
                            style=mockup_style_key,
                            logo_application=logo_application_key,
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
                            display_results(result)
                            
                        elif result["status"] == "partial_success":
                            st.warning("⚠️ Частичный успех - использованы локальные мокапы")
                            display_results(result)
                            
                        else:
                            st.error("❌ Ошибка генерации мокапов")
                            if "text_response" in result:
                                with st.expander("📝 Текстовый ответ от Gemini"):
                                    st.write(result["text_response"])
                            st.error(result.get("error", "Неизвестная ошибка"))
                            
                            # Показываем fallback мокапы даже при ошибке
                            if "mockups" in result:
                                display_results(result)
                    
                    except Exception as e:
                        st.error(f"❌ Критическая ошибка: {e}")
                        st.error("Попробуйте перезагрузить страницу или проверить изображения")
    
    else:
        st.info("👆 Загрузите изображение товара и логотип для начала генерации")
    
            
    

def display_results(result: dict):
    """Отображение результатов генерации с динамическим обновлением"""
    
    # Сохраняем результат в session_state для галереи
    st.session_state.last_result = result
    st.session_state.last_generation_result = result
    
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
                upload_to_server(mockup["image_data"], gallery_entry["metadata"], mockup.get("description", ""))
                
                # Загружаем на FTP если включено
                upload_to_ftp(mockup["image_data"], gallery_entry["metadata"], mockup.get("description", ""))

def display_mockups_dynamically(mockups: dict, result: dict):
    """Динамическое отображение мокапов с возможностью обновления"""
    
    # Проверяем, что mockups не пустой и содержит gemini_mockups
    if not mockups or "gemini_mockups" not in mockups or not mockups["gemini_mockups"]:
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
                            from PIL import Image
                            import io
                            from image_processor import ImageProcessor
                            
                            # image_data уже является bytes от Gemini
                            image_data = mockup["image_data"]
                            image = Image.open(io.BytesIO(image_data))
                            
                            # Конвертируем в RGB для совместимости с JPEG
                            if image.mode in ('RGBA', 'LA', 'P'):
                                from image_processor import ImageProcessor
                                processor = ImageProcessor()
                                image = processor.convert_to_rgb(image)
                                # Обновляем image_data
                                img_byte_arr = io.BytesIO()
                                image.save(img_byte_arr, format='JPEG', quality=95)
                                image_data = img_byte_arr.getvalue()
                            
                            # Увеличенное превью результата для лучшего просмотра
                            st.image(image, use_container_width=True)
                            
                            # Кнопки управления
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Кнопка скачивания
                                st.download_button(
                                    label="Скачать",
                                    data=image_data,
                                    file_name=f"ai_mockup_{i+1}.jpg",
                                    mime="image/jpeg",
                                    key=f"download_ai_{i+1}",
                                    use_container_width=True
                                )
                            
                            with col2:
                                # Кнопка пересоздания с динамическим обновлением
                                if st.button(f"Перегенерировать мокап {i+1}", key=f"regenerate_{i+1}", use_container_width=True, help="Создать новый мокап с теми же параметрами"):
                                    # Сохраняем параметры для перегенерации
                                    st.session_state.regenerate_params = {
                                        "mockup_index": i,
                                        "original_mockup": mockup,
                                        "original_result": result,
                                        "container_key": container_key
                                    }
                                    st.rerun()
                            
                            # Показываем текстовый ответ если есть
                            if "text_response" in mockup and mockup["text_response"]:
                                with st.expander(f"📝 Текстовый ответ от Gemini (мокап {i+1})"):
                                    st.write(mockup["text_response"])
                        
                        except Exception as e:
                            st.error(f"❌ Ошибка отображения мокапа {i+1}: {str(e)}")
    
    # Локальные мокапы (если есть)
    if "local_mockups" in mockups:
        local_mockups = mockups["local_mockups"]
        
        if local_mockups:
            st.subheader("🏠 Локальные мокапы")
            
            for i, mockup in enumerate(local_mockups):
                if "image" in mockup:
                    st.image(mockup["image"], caption=f"Локальный мокап {i+1}", use_container_width=True)
                    
                    # Кнопка скачивания для локальных мокапов
                    if "image" in mockup:
                        # Конвертируем PIL Image в bytes
                        import io
                        img_byte_arr = io.BytesIO()
                        
                        image = mockup["image"]
                        # Убеждаемся, что изображение в RGB режиме для JPEG
                        if image.mode == 'RGBA':
                            # Создаем белый фон для RGBA изображений
                            background = Image.new('RGB', image.size, (255, 255, 255))
                            background.paste(image, mask=image.split()[-1])
                            image = background
                        elif image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        image.save(img_byte_arr, format='JPEG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        st.download_button(
                            label=f"📥 Скачать локальный мокап {i+1}",
                            data=img_byte_arr,
                            file_name=f"local_mockup_{i+1}.jpg",
                            mime="image/jpeg",
                            key=f"download_local_{i+1}",
                            use_container_width=True
                        )

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
            generator = get_mockup_generator()
            
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
            
            # Заменяем только выбранный мокап в оригинальном результате
            if new_result and "mockups" in new_result and "gemini_mockups" in new_result["mockups"]:
                new_mockups = new_result["mockups"]["gemini_mockups"]
                if new_mockups and len(new_mockups) > 0:
                    # Убеждаемся, что оригинальный результат имеет правильную структуру
                    if "mockups" not in original_result:
                        original_result["mockups"] = {}
                    if "gemini_mockups" not in original_result["mockups"]:
                        original_result["mockups"]["gemini_mockups"] = []
                    
                    # Заменяем конкретный мокап
                    if mockup_index < len(original_result["mockups"]["gemini_mockups"]):
                        original_result["mockups"]["gemini_mockups"][mockup_index] = new_mockups[0]
                    else:
                        # Если индекс больше длины массива, добавляем в конец
                        original_result["mockups"]["gemini_mockups"].append(new_mockups[0])
                    
                    # Обновляем session_state
                    st.session_state.last_result = original_result
                    st.session_state.last_generation_result = original_result
                    
                    # Обновляем статус
                    status_text.text("🎉 Мокап успешно пересоздан!")
                    progress_bar.progress(100)
                    time.sleep(1)
                    
                    # Очищаем прогресс-бар и статус
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Обновляем отображение мокапа
                    update_mockup_display(mockup_index, new_mockups[0], original_result, container_key)
                    
                    st.success(f"✅ Мокап {mockup_index + 1} пересоздан!")
                else:
                    st.error("❌ Не удалось получить новый мокап")
            else:
                # Fallback: создаем новую структуру если её нет
                if not new_result:
                    st.error("❌ Ошибка: генератор вернул пустой результат")
                elif "mockups" not in new_result:
                    st.error("❌ Ошибка: в результате отсутствует ключ 'mockups'")
                else:
                    st.error("❌ Ошибка при генерации нового мокапа")
        
        except Exception as e:
            st.error(f"❌ Ошибка пересоздания: {str(e)}")
            progress_bar.empty()
            status_text.empty()

def update_mockup_display(mockup_index: int, new_mockup: dict, result: dict, container_key: str):
    """Обновление отображения конкретного мокапа"""
    
    # Проверяем, что new_mockup не пустой
    if not new_mockup:
        st.error("❌ Ошибка: пустой мокап для обновления")
        return
    
    # Получаем контейнер
    if container_key not in st.session_state.mockup_containers:
        st.error(f"❌ Ошибка: контейнер {container_key} не найден")
        return
        
    mockup_container = st.session_state.mockup_containers[container_key]
    
    # Обновляем содержимое контейнера
    with mockup_container.container():
        if "description" in new_mockup:
            st.write(f"**Вариант {mockup_index+1}:** {new_mockup['description']}")
        
        # Если есть изображение от Gemini
        if "image_data" in new_mockup:
            try:
                from PIL import Image
                import io
                from image_processor import ImageProcessor
                
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
                
                # Увеличенное превью результата для лучшего просмотра
                st.image(image, caption=f"AI-мокап {mockup_index+1}", use_container_width=True)
                
                # Кнопки управления
                col1, col2 = st.columns(2)
                
                with col1:
                    # Кнопка скачивания
                    st.download_button(
                        label=f"📥 Скачать AI-мокап {mockup_index+1}",
                        data=image_data,
                        file_name=f"ai_mockup_{mockup_index+1}.jpg",
                        mime="image/jpeg",
                        key=f"download_ai_{mockup_index+1}_new",
                        use_container_width=True
                    )
                
                with col2:
                    # Кнопка пересоздания с динамическим обновлением
                    if st.button(f"🎨 Перегенерировать мокап {mockup_index+1}", key=f"regenerate_{mockup_index+1}_new", use_container_width=True, help="Создать новый мокап с теми же параметрами"):
                        regenerate_mockup_dynamically(mockup_index, new_mockup, result, container_key)
                
                # Показываем текстовый ответ если есть
                if "text_response" in new_mockup and new_mockup["text_response"]:
                    with st.expander(f"📝 Текстовый ответ от Gemini (мокап {mockup_index+1})"):
                        st.write(new_mockup["text_response"])
            
            except Exception as e:
                st.error(f"❌ Ошибка отображения мокапа {mockup_index+1}: {str(e)}")
    
    # Информация о результате
    st.info(f"Источник: {result.get('source', 'unknown')} | "
            f"Время обработки: {result.get('processing_time', 0):.2f}с")

def creative_generation_interface():
    """Интерфейс для креативного генератора концепций"""
    
    st.markdown("### Креативный генератор концепций")
    st.markdown("Создайте 5 уникальных концепций товара на основе логотипа и брендбука")
    
    # Три колонки для загрузки файлов
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Товар**")
        product_files = st.file_uploader(
            "Загрузите товар с разных ракурсов",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="creative_product",
            accept_multiple_files=True,
            help="Загрузите несколько фотографий товара с разных ракурсов для лучшего анализа"
        )
        
        if product_files:
            # Обрабатываем все изображения
            processed_images = []
            for i, product_file in enumerate(product_files):
                product_image = Image.open(product_file)
                # Конвертируем в RGB для совместимости с JPEG
                if product_image.mode in ('RGBA', 'LA', 'P'):
                    from image_processor import ImageProcessor
                    processor = ImageProcessor()
                    product_image = processor.convert_to_rgb(product_image)
                processed_images.append(product_image)
            
            st.session_state.creative_product_images = processed_images
            
            # Показываем превью всех изображений
            st.markdown(f"**Загружено {len(processed_images)} фотографий:**")
            for i, product_image in enumerate(processed_images):
                preview_size = (120, 120)
                preview_image = product_image.copy()
                preview_image.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_image, caption=f"Ракурс {i+1}", width=120)
                st.caption(f"{product_image.size[0]}x{product_image.size[1]}")
        elif "creative_product_images" in st.session_state:
            processed_images = st.session_state.creative_product_images
            st.markdown(f"**Загружено {len(processed_images)} фотографий:**")
            for i, product_image in enumerate(processed_images):
                preview_size = (120, 120)
                preview_image = product_image.copy()
                preview_image.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_image, caption=f"Ракурс {i+1}", width=120)
                st.caption(f"{product_image.size[0]}x{product_image.size[1]}")
    
    with col2:
        st.markdown("**Логотип**")
        logo_file = st.file_uploader(
            "Загрузите логотип",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="creative_logo"
        )
        
        if logo_file:
            logo_image = Image.open(logo_file)
            # Конвертируем в RGB для совместимости с JPEG
            if logo_image.mode in ('RGBA', 'LA', 'P'):
                from image_processor import ImageProcessor
                processor = ImageProcessor()
                logo_image = processor.convert_to_rgb(logo_image)
            st.session_state.creative_logo_image = logo_image
            preview_size = (120, 120)
            preview_logo = logo_image.copy()
            preview_logo.thumbnail(preview_size, Image.LANCZOS)
            st.image(preview_logo, caption="Логотип", width=120)
            st.caption(f"{logo_image.size[0]}x{logo_image.size[1]}")
        elif "creative_logo_image" in st.session_state:
            logo_image = st.session_state.creative_logo_image
            preview_size = (120, 120)
            preview_logo = logo_image.copy()
            preview_logo.thumbnail(preview_size, Image.LANCZOS)
            st.image(preview_logo, caption="Логотип", width=120)
            st.caption(f"{logo_image.size[0]}x{logo_image.size[1]}")
    
    with col3:
        st.markdown("**Брендбук**")
        brandbook_files = st.file_uploader(
            "Загрузите брендбук (PDF или изображения)",
            type=['pdf', 'jpg', 'jpeg', 'png', 'webp'],
            key="creative_brandbook",
            accept_multiple_files=True,
            help="PDF файл или изображения с брендбуком"
        )
        
        if brandbook_files:
            # Не сохраняем в session_state, работаем напрямую
            st.success(f"Загружено файлов: {len(brandbook_files)}")
    
    # Дополнительное описание
    st.markdown("---")
    st.markdown("### Дополнительные требования")
    custom_prompt = st.text_area(
        "Дополнительное описание концепций",
        placeholder="Опишите дополнительные требования к концепциям...",
        key="creative_custom_prompt",
        help="Дополнительные требования, которые будут добавлены к каждому промпту"
    )
    
    # Кнопка генерации
    st.markdown("---")
    if st.button("Сгенерировать концепции", key="creative_generate", use_container_width=True, type="primary"):
        if not st.session_state.get('creative_product_images') or not st.session_state.get('creative_logo_image'):
            st.error("❌ Пожалуйста, загрузите товар (хотя бы одну фотографию) и логотип")
            return
        
        # Брендбук не обязателен, но если загружен - будет использован
        if not brandbook_files:
            st.info("ℹ️ Брендбук не загружен - ищем информацию о бренде в интернете на основе логотипа...")
        
        # Генерируем концепции (используем оптимизированную версию если включена)
        from config import UNIFIED_ANALYSIS_ENABLED
        if UNIFIED_ANALYSIS_ENABLED:
            generate_creative_concepts_optimized(brandbook_files)
        else:
            generate_creative_concepts(brandbook_files)

def search_brand_info_online(logo_image):
    """Ищет информацию о бренде в интернете на основе логотипа"""
    try:
        # Конвертируем логотип в base64 для отправки в Gemini
        import io
        import base64
        
        logo_buffer = io.BytesIO()
        logo_image.save(logo_buffer, format='JPEG', quality=95)
        logo_base64 = base64.b64encode(logo_buffer.getvalue()).decode()
        
        # Создаем промпт для анализа логотипа
        logo_analysis_prompt = """
        🚨 ВАЖНО: Все генерируемые изображения должны быть 1024x1024 пикселей (квадратные) 🚨
        
        Проанализируй этот логотип и найди информацию о бренде:
        
        1. Определи название бренда (если видно)
        2. Проанализируй цветовую палитру логотипа
        3. Определи стиль дизайна (минимализм, классика, современный, ретро и т.д.)
        4. Оцени общее настроение бренда (серьезный, игривый, премиум, доступный)
        5. Предложи дополнительные цвета, которые подходят к этому бренду
        6. Определи целевую аудиторию бренда
        7. Предложи стили дизайна, которые подходят этому бренду
        
        Ответь структурированно, чтобы эту информацию можно было использовать для создания концепций товара.
        """
        
        # Отправляем в Gemini для анализа
        from gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        # Создаем файл для анализа
        files_for_analysis = [{
            'data': logo_buffer.getvalue(),
            'mime_type': 'image/jpeg',
            'name': 'logo_analysis.jpg'
        }]
        
        brand_analysis = gemini_client.generate_with_files(logo_analysis_prompt, files_for_analysis)
        
        if brand_analysis:
            return brand_analysis
        else:
            return None
            
    except Exception as e:
        print(f"Ошибка поиска информации о бренде: {e}")
        return None

def generate_creative_concepts_optimized(brandbook_files):
    """Оптимизированная версия генерации креативных концепций (объединенный анализ)"""
    
    # Получаем данные из session_state
    product_images = st.session_state.creative_product_images
    logo_image = st.session_state.creative_logo_image
    custom_prompt = st.session_state.get('creative_custom_prompt', '')
    
    # Ищем информацию о бренде, если брендбук не загружен
    brand_analysis = None
    if not brandbook_files:
        st.info("🔍 Анализируем логотип для поиска информации о бренде...")
        brand_analysis = search_brand_info_online(logo_image)
        if brand_analysis:
            st.success("✅ Информация о бренде найдена")
            with st.expander("🎨 Анализ бренда", expanded=False):
                st.write(brand_analysis)
    
    st.info("Анализируем товар, бренд и создаем концепции в одном запросе...")
    
    try:
        # Создаем объединенный промпт для всего анализа
        unified_prompt = f"""
        Ты - эксперт по мерчендайзингу и дизайну товаров. Выполни полный анализ и создай 5 уникальных концепций для товара.
        
        {f"АНАЛИЗ БРЕНДА (найден в интернете):\n{brand_analysis}\n" if brand_analysis else ""}
        
        ЗАДАЧИ:
        1. Проанализируй товар: тип, материал, цвет, размер, целевую аудиторию
        2. Изучи современные тренды в мерчендайзинге 2024-2025 для этого типа товара
        3. {f"Используй информацию о бренде выше" if brand_analysis else "Проанализируй логотип и определи стиль бренда"}
        4. {f"Если предоставлен брендбук - изучи его и выдели основные элементы бренда" if brandbook_files else ""}
        5. Создай 5 уникальных концепций товара
        
        ТРЕБОВАНИЯ К КОНЦЕПЦИЯМ:
        - Реалистичные и не требующие сложного исполнения
        - Современные, актуальные и дизайнерские
        - Интегрируют логотип креативно
        - Не изменяют сам товар, только добавляют элементы дизайна
        - Каждая концепция уникальна
        - Яркие, цепляющие и продающие
        - Учитывают тренды для данного типа товара
        
        {f"ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ: {custom_prompt}" if custom_prompt else ""}
        
        Верни 5 промптов для создания концепций, каждый на отдельной строке, начинающейся с номера (1., 2., 3., 4., 5.)
        Каждый промпт должен быть детальным и включать конкретные элементы дизайна, цвета, расположение, стиль.
        """
        
        # Подготавливаем все файлы для анализа
        files_to_analyze = []
        
        # Добавляем все изображения товара
        for i, product_image in enumerate(product_images):
            import io
            buffer = io.BytesIO()
            product_image.save(buffer, format='JPEG', quality=60)
            files_to_analyze.append({
                'data': buffer.getvalue(),
                'mime_type': 'image/jpeg',
                'name': f'product_angle_{i+1}.jpg'
            })
        
        # Добавляем логотип
        logo_buffer = io.BytesIO()
        logo_image.save(logo_buffer, format='JPEG', quality=60)
        files_to_analyze.append({
            'data': logo_buffer.getvalue(),
            'mime_type': 'image/jpeg',
            'name': 'logo.jpg'
        })
        
        # Добавляем брендбук (если есть)
        for i, brandbook_file in enumerate(brandbook_files):
            files_to_analyze.append({
                'data': brandbook_file.getvalue(),
                'mime_type': brandbook_file.type,
                'name': f'brandbook_{i}.pdf' if brandbook_file.type == 'application/pdf' else f'brandbook_{i}.jpg'
            })
        
        # Отправляем объединенный запрос
        from gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        concepts_response = gemini_client.generate_with_files(unified_prompt, files_to_analyze)
        
        if not concepts_response or not concepts_response.strip():
            st.error("❌ Не удалось получить концепции от анализатора")
            return
        
        # Парсим концепции
        concepts = []
        lines = concepts_response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or 
                        line.startswith('4.') or line.startswith('5.')):
                # Убираем номер
                concept = line.split('.', 1)[1].strip()
                concepts.append(concept)
        
        if len(concepts) < 5:
            st.warning(f"⚠️ Получено только {len(concepts)} концепций вместо 5")
        
        # Генерируем мокапы для каждой концепции
        st.info(f"Создаем {len(concepts)} концепций...")
        
        generated_concepts = []
        for i, concept in enumerate(concepts):
            st.write(f"🎨 Концепция {i+1}: {concept}")
            
            # Используем первое изображение товара для генерации мокапа
            main_product_image = product_images[0]
            
            # Генерируем мокап
            from mockup_generator import get_mockup_generator
            generator = get_mockup_generator()
            
            result = generator.generate_mockups(
                product_image=main_product_image,
                logo_image=logo_image,
                style="modern",
                logo_application="embroidery",
                custom_prompt=concept,
                product_color="как на фото",
                product_angle="как на фото",
                logo_position="центр",
                logo_size="средний",
                logo_color="как на фото"
            )
            
            if result["status"] == "success" and result["mockups"]["gemini_mockups"]:
                mockup = result["mockups"]["gemini_mockups"][0]
                generated_concepts.append({
                    "index": i + 1,
                    "concept": concept,
                    "mockup": mockup
                })
            else:
                st.error(f"❌ Ошибка генерации концепции {i+1}")
        
        # Сохраняем результаты
        st.session_state.creative_generated_concepts = generated_concepts
        st.success(f"✅ Создано {len(generated_concepts)} концепций!")
        
    except Exception as e:
        st.error(f"❌ Ошибка оптимизированной генерации концепций: {e}")
        st.info("🔄 Переключаемся на стандартный режим...")
        # Fallback на стандартную версию
        generate_creative_concepts(brandbook_files)

def generate_creative_concepts(brandbook_files):
    """Генерирует 5 креативных концепций товара (стандартная версия)"""
    
    # Получаем данные из session_state
    product_images = st.session_state.creative_product_images
    logo_image = st.session_state.creative_logo_image
    custom_prompt = st.session_state.get('creative_custom_prompt', '')
    
    # Ищем информацию о бренде, если брендбук не загружен
    brand_analysis = None
    if not brandbook_files:
        st.info("🔍 Анализируем логотип для поиска информации о бренде...")
        brand_analysis = search_brand_info_online(logo_image)
        if brand_analysis:
            st.success("✅ Информация о бренде найдена")
            with st.expander("🎨 Анализ бренда", expanded=False):
                st.write(brand_analysis)
        else:
            st.warning("⚠️ Не удалось найти информацию о бренде")
    
    # Показываем сохраненные результаты, если они есть
    if "creative_generated_concepts" in st.session_state and st.session_state.creative_generated_concepts:
        st.markdown("### Результаты генерации")
        
        # Создаем сетку концептов
        cols = st.columns(5)  # 5 колонок для 5 концептов
        
        for i, concept_data in enumerate(st.session_state.creative_generated_concepts):
            with cols[i]:
                st.markdown(f"**Концепция {concept_data['index']}**")
                
                # Показываем превью изображения
                mockup = concept_data['mockup']
                if "image_data" in mockup:
                    # Создаем превью изображения 600x600
                    from PIL import Image
                    import io
                    full_image = Image.open(io.BytesIO(mockup["image_data"]))
                    preview_image = full_image.copy()
                    preview_image.thumbnail((600, 600), Image.LANCZOS)
                    
                    # Показываем превью
                    st.image(preview_image, use_container_width=True, caption=f"Концепция {concept_data['index']}")
                
                # Кнопки для показа полной версии и скачивания
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Подробнее", key=f"show_concept_saved_{i}_{concept_data['index']}", use_container_width=True):
                        st.session_state[f"show_concept_{concept_data['index']}"] = True
                        st.rerun()
                with col2:
                    # Создаем кнопку скачивания напрямую
                    mockup = concept_data['mockup']
                    if "image_data" in mockup:
                        st.download_button(
                            label="Скачать",
                            data=mockup["image_data"],
                            file_name=f"concept_{concept_data['index']}.jpg",
                            mime="image/jpeg",
                            key=f"download_btn_saved_{i}_{concept_data['index']}",
                            use_container_width=True
                        )
        
        # Показываем полные версии концептов
        for concept_data in st.session_state.creative_generated_concepts:
            if st.session_state.get(f"show_concept_{concept_data['index']}", False):
                with st.expander(f"Концепция {concept_data['index']} - Полная версия", expanded=True):
                    st.write(concept_data['concept'])
                    
                    # Показываем полное изображение 1200x1200
                    mockup = concept_data['mockup']
                    if "image_data" in mockup:
                        full_image = Image.open(io.BytesIO(mockup["image_data"]))
                        # Изменяем размер до 1200x1200 с сохранением пропорций
                        full_image.thumbnail((1200, 1200), Image.LANCZOS)
                        st.image(full_image, use_container_width=True)
                    
                    # Кнопки действий
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Скачать",
                            data=mockup["image_data"],
                            file_name=f"concept_{concept_data['index']}.jpg",
                            mime="image/jpeg",
                            key=f"download_concept_{concept_data['index']}_btn"
                        )
                    
                    with col2:
                        if st.button(f"Перегенерировать", key=f"regenerate_concept_{concept_data['index']}"):
                            st.session_state.regenerate_creative_concept = concept_data['index']
                            st.rerun()
                    
                    # Кнопка закрытия
                    if st.button(f"Закрыть", key=f"close_concept_{concept_data['index']}"):
                        st.session_state[f"show_concept_{concept_data['index']}"] = False
                        st.rerun()
        
        # Если есть сохраненные результаты, показываем их, но не прерываем выполнение
        # return
    
    st.info("Анализируем брендбук и создаем концепции...")
    
    try:
        # Создаем улучшенный промпт для анализатора с современными стандартами
        analysis_prompt = f"""
        Ты - эксперт по мерчендайзингу и дизайну товаров. Проанализируй предоставленные файлы брендбука и создай 5 уникальных концепций для товара.
        
        {f"АНАЛИЗ БРЕНДА (найден в интернете):\n{brand_analysis}\n" if brand_analysis else ""}
        
        ПЕРЕД СОЗДАНИЕМ КОНЦЕПЦИЙ:
        1. Изучи современные тренды в мерчендайзинге 2024-2025
        2. Проанализируй товар и определи его ключевые особенности
        3. Если предоставлен брендбук - изучи его и выдели основные элементы бренда
        4. {f"Используй информацию о бренде выше для создания концепций в стиле бренда" if brand_analysis else "Создай концепции на основе логотипа и трендов"}
        5. Подумай о том, как сделать концепции яркими и цепляющими
        
        ТРЕБОВАНИЯ К КОНЦЕПЦИЯМ:
        - Должны быть реалистичными и не требовать сложного исполнения
        - Должны быть современными, актуальными и дизайнерскими
        - Должны интегрировать логотип в товар креативно
        - Не должны изменять сам товар, только добавлять элементы дизайна
        - Каждая концепция должна быть уникальной и отличаться от других
        - Должны быть яркими, цепляющими и продающими
        - Учитывай современные тренды: минимализм, экологичность, персонализация, интерактивность
        
        ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ: {custom_prompt}
        
        Верни 5 промптов для создания концепций, каждый на отдельной строке, начинающейся с номера (1., 2., 3., 4., 5.)
        Каждый промпт должен быть детальным и включать конкретные элементы дизайна, цвета, расположение, стиль.
        """
        
        # Сначала анализируем товар отдельно
        st.info("Анализируем товар и современные тренды...")
        
        # Анализ товара с фокусом на тренды конкретного типа товара
        product_analysis_prompt = f"""
        🚨 ВАЖНО: Все генерируемые изображения должны быть 1024x1024 пикселей (квадратные) 🚨
        
        Проанализируй эти фотографии товара с разных ракурсов и определи:
        
        ОСНОВНАЯ ИНФОРМАЦИЯ О ТОВАРЕ:
        1. Тип товара и его ключевые особенности
        2. Материал и текстуру
        3. Цветовую гамму
        4. Размер и пропорции
        5. Целевую аудиторию
        6. Особенности формы и конструкции товара
        
        ТРЕНДЫ ДЛЯ КОНКРЕТНОГО ТИПА ТОВАРА:
        7. Современные тренды в дизайне именно этого типа товара (футболки, толстовки, кружки и т.д.)
        8. Популярные стили нанесения для данного типа товара
        9. Актуальные цветовые решения для этого типа товара
        10. Модные элементы дизайна, которые подходят именно к этому товару
        11. Тренды в позиционировании логотипа на данном типе товара
        12. Современные техники печати/вышивки для этого типа товара
        
        ВОЗМОЖНОСТИ ДЛЯ ДИЗАЙНА:
        13. Лучшие ракурсы для размещения логотипа
        14. Потенциал для различных стилей дизайна
        15. Креативные идеи размещения элементов дизайна
        16. Возможности комбинирования с паттернами или текстурами
        
        Ответь детально, с фокусом на специфику именно этого типа товара.
        """
        
        # Отправляем в анализатор
        from gemini_client import GeminiClient
        gemini_client = GeminiClient()
        
        # Конвертируем все изображения товара в bytes для анализа
        import io
        product_files_for_analysis = []
        for i, product_image in enumerate(product_images):
            product_buffer = io.BytesIO()
            product_image.save(product_buffer, format='JPEG', quality=95)
            product_image_bytes = product_buffer.getvalue()
            product_files_for_analysis.append({
                'data': product_image_bytes,
                'mime_type': 'image/jpeg',
                'name': f'product_angle_{i+1}.jpg'
            })
        
        # Анализируем товар
        product_analysis = gemini_client.generate_with_files(product_analysis_prompt, product_files_for_analysis)
        
        if product_analysis:
            st.success("✅ Анализ товара завершен")
            with st.expander("📊 Анализ товара", expanded=False):
                st.write(product_analysis)
        
        # Теперь создаем концепции с учетом анализа товара и бренда
        st.info("Создаем концепции на основе детального анализа товара и бренда...")
        
        # Обновляем основной промпт с учетом анализа товара и бренда
        if product_analysis:
            analysis_prompt = f"""
            Ты - эксперт по мерчендайзингу и дизайну товаров. Проанализируй предоставленные файлы брендбука и создай 5 уникальных концепций для товара.
            
            АНАЛИЗ ТОВАРА (уже выполнен):
            {product_analysis}
            
            {f"АНАЛИЗ БРЕНДА (найден в интернете):\n{brand_analysis}\n" if brand_analysis else ""}
            
            ПЕРЕД СОЗДАНИЕМ КОНЦЕПЦИЙ:
            1. Изучи современные тренды в мерчендайзинге 2024-2025
            2. Используй результаты анализа товара выше для создания релевантных концепций
            3. Если предоставлен брендбук - изучи его и выдели основные элементы бренда
            4. {f"Используй информацию о бренде выше для создания концепций в стиле бренда" if brand_analysis else "Создай концепции на основе логотипа и трендов"}
            5. Подумай о том, как сделать концепции яркими и цепляющими, учитывая специфику данного типа товара
            
            ТРЕБОВАНИЯ К КОНЦЕПЦИЯМ:
            - Должны быть реалистичными и не требовать сложного исполнения
            - Должны быть современными, актуальными и дизайнерскими
            - Должны интегрировать логотип в товар креативно, учитывая особенности данного типа товара
            - Не должны изменять сам товар, только добавлять элементы дизайна
            - Каждая концепция должна быть уникальной и отличаться от других
            - Должны быть яркими, цепляющими и продающими
            - Должны учитывать тренды именно для этого типа товара
            
            {f"ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ: {custom_prompt}" if custom_prompt else ""}
            
            Верни 5 промптов для создания концепций, каждый на отдельной строке, начинающейся с номера (1., 2., 3., 4., 5.)
            Каждый промпт должен быть детальным и включать конкретные элементы дизайна, цвета, расположение, стиль, учитывая специфику данного типа товара.
            """
        
        # Подготавливаем файлы для анализа
        files_to_analyze = []
        
        # Добавляем все изображения товара
        # Конвертируем PIL Image в bytes для отправки
        import io
        
        # Все ракурсы товара
        for i, product_image in enumerate(product_images):
            product_buffer = io.BytesIO()
            product_image.save(product_buffer, format='JPEG', quality=95)
            files_to_analyze.append({
                'data': product_buffer.getvalue(),
                'mime_type': 'image/jpeg',
                'name': f'product_angle_{i+1}.jpg'
            })
        
        # Логотип
        logo_buffer = io.BytesIO()
        logo_image.save(logo_buffer, format='JPEG', quality=95)
        files_to_analyze.append({
            'data': logo_buffer.getvalue(),
            'mime_type': 'image/jpeg', 
            'name': 'logo.jpg'
        })
        
        # Добавляем файлы брендбука (если загружены)
        if brandbook_files:
            for i, file in enumerate(brandbook_files):
                if file.type == 'application/pdf':
                    files_to_analyze.append({
                        'data': file,
                        'mime_type': 'application/pdf',
                        'name': f'brandbook_{i}.pdf'
                    })
                else:
                    # Конвертируем изображения в RGB если нужно
                    from PIL import Image
                    import io
                    image = Image.open(file)
                    if image.mode in ['RGBA', 'LA', 'P']:
                        from image_processor import ImageProcessor
                        processor = ImageProcessor()
                        image = processor.convert_to_rgb(image)
                    
                    # Конвертируем в bytes
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=95)
                    files_to_analyze.append({
                        'data': buffer.getvalue(),
                        'mime_type': 'image/jpeg',
                        'name': f'brandbook_{i}.jpg'
                    })
        
        # Получаем концепции от анализатора
        concepts_response = gemini_client.generate_with_files(analysis_prompt, files_to_analyze)
        
        if not concepts_response or not concepts_response.strip():
            st.error("❌ Не удалось получить концепции от анализатора")
            return
        
        # Парсим концепции
        concepts = []
        lines = concepts_response.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or 
                        line.startswith('4.') or line.startswith('5.')):
                # Убираем номер
                concept = line.split('.', 1)[1].strip()
                concepts.append(concept)
        
        if len(concepts) < 5:
            st.warning(f"⚠️ Получено только {len(concepts)} концепций вместо 5")
        
        # Показываем концепции
        st.markdown("### Сгенерированные концепции")
        for i, concept in enumerate(concepts[:5], 1):
            with st.expander(f"Концепция {i}", expanded=True):
                st.write(concept)
        
        # Генерируем изображения для каждой концепции
        st.markdown("### Генерация изображений концепций")
        
        # Получаем генератор мокапов
        from mockup_generator import MockupGenerator
        generator = MockupGenerator()
        
        # Генерируем изображения
        generated_concepts = []
        for i, concept in enumerate(concepts[:5], 1):
            st.info(f"Генерируем концепцию {i}...")
            
            # Создаем промпт для генерации
            generation_prompt = f"""
            {concept}
            
            Создай реалистичный мокап товара с этой концепцией.
            Интегрируй логотип в дизайн согласно концепции.
            
            🚨 КРИТИЧЕСКИ ВАЖНО: РАЗМЕР ИЗОБРАЖЕНИЯ 🚨
            - Сгенерируй изображение ТОЛЬКО в разрешении 1024x1024 пикселей
            - Изображение должно быть КВАДРАТНЫМ (1:1)
            - НЕ создавай горизонтальные или вертикальные изображения
            - Финальное изображение должно быть идеально квадратным
            
            {custom_prompt}
            """
            
            # Используем первое изображение товара для генерации мокапа
            main_product_image = product_images[0]
            
            # Генерируем мокап
            result = generator.generate_mockups(
                product_image=main_product_image,
                logo_image=logo_image,
                style="modern",
                logo_application="embroidery",
                custom_prompt=generation_prompt,
                product_color="как на фото",
                product_angle="спереди",
                logo_position="центр",
                logo_size="средний",
                logo_color="как на фото"
            )
            
            if result and "mockups" in result and "gemini_mockups" in result["mockups"]:
                mockups = result["mockups"]["gemini_mockups"]
                if mockups:
                    # Изменяем размер изображения до 1200x1200
                    mockup = mockups[0].copy()
                    if "image_data" in mockup:
                        from PIL import Image
                        import io
                        # Открываем изображение
                        image = Image.open(io.BytesIO(mockup["image_data"]))
                        # Изменяем размер до 1200x1200 с сохранением пропорций
                        image.thumbnail((1200, 1200), Image.LANCZOS)
                        # Сохраняем обратно в bytes
                        buffer = io.BytesIO()
                        image.save(buffer, format='JPEG', quality=95)
                        mockup["image_data"] = buffer.getvalue()
                    
                    # Загружаем на FTP
                    try:
                        from services.upload_services import upload_to_ftp
                        upload_to_ftp(
                            image_data=mockup["image_data"],
                            metadata={
                                'concept': concept,
                                'generation_type': 'creative',
                                'concept_index': i,
                                'custom_prompt': custom_prompt
                            },
                            description=f"Креативная концепция {i+1}: {concept[:50]}..."
                        )
                        # Концепция загружена на FTP (без уведомления)
                    except Exception as e:
                        st.warning(f"⚠️ Не удалось загрузить концепцию {i+1} на FTP: {str(e)}")
                    
                    generated_concepts.append({
                        'concept': concept,
                        'mockup': mockup,
                        'index': i
                    })
        
        # Сохраняем результаты в session_state
        st.session_state.creative_generated_concepts = generated_concepts
        
        # Отображаем результаты (используем сохраненные или новые)
        display_concepts = st.session_state.get('creative_generated_concepts', generated_concepts)
        if display_concepts:
            st.markdown("### Результаты генерации")
            
            # Создаем сетку концептов
            cols = st.columns(5)  # 5 колонок для 5 концептов
            
            for i, concept_data in enumerate(display_concepts):
                with cols[i]:
                    st.markdown(f"**Концепция {concept_data['index']}**")
                    
                    # Показываем превью изображения
                    mockup = concept_data['mockup']
                    if "image_data" in mockup:
                        # Создаем превью изображения 600x600
                        from PIL import Image
                        import io
                        full_image = Image.open(io.BytesIO(mockup["image_data"]))
                        preview_image = full_image.copy()
                        preview_image.thumbnail((600, 600), Image.LANCZOS)
                        
                        # Показываем превью
                        st.image(preview_image, use_container_width=True, caption=f"Концепция {concept_data['index']}")
                    
                    # Кнопки для показа полной версии и скачивания
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Подробнее", key=f"show_concept_new_{i}_{concept_data['index']}", use_container_width=True):
                            st.session_state[f"show_concept_{concept_data['index']}"] = True
                            st.rerun()
                    with col2:
                        # Создаем кнопку скачивания напрямую
                        mockup = concept_data['mockup']
                        if "image_data" in mockup:
                            st.download_button(
                                label="Скачать",
                                data=mockup["image_data"],
                                file_name=f"concept_{concept_data['index']}.jpg",
                                mime="image/jpeg",
                                key=f"download_btn_new_{i}_{concept_data['index']}",
                                use_container_width=True
                            )
            
            # Показываем полные версии концептов
            for concept_data in display_concepts:
                if st.session_state.get(f"show_concept_{concept_data['index']}", False):
                    with st.expander(f"Концепция {concept_data['index']} - Полная версия", expanded=True):
                        st.write(concept_data['concept'])
                        
                        # Показываем полное изображение 1200x1200
                        mockup = concept_data['mockup']
                        if "image_data" in mockup:
                            full_image = Image.open(io.BytesIO(mockup["image_data"]))
                            # Изменяем размер до 1200x1200 с сохранением пропорций
                            full_image.thumbnail((1200, 1200), Image.LANCZOS)
                            st.image(full_image, use_container_width=True)
                        
                        # Кнопки действий
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="Скачать",
                                data=mockup["image_data"],
                                file_name=f"concept_{concept_data['index']}.jpg",
                                mime="image/jpeg",
                                key=f"download_concept_{concept_data['index']}_btn"
                            )
                        
                        with col2:
                            if st.button(f"Перегенерировать", key=f"regenerate_concept_{concept_data['index']}"):
                                st.session_state.regenerate_creative_concept = concept_data['index']
                                st.rerun()
                        
                        # Кнопка закрытия
                        if st.button(f"Закрыть", key=f"close_concept_{concept_data['index']}"):
                            st.session_state[f"show_concept_{concept_data['index']}"] = False
                            st.rerun()
        else:
            st.error("❌ Не удалось сгенерировать изображения концепций")
            
    except Exception as e:
        st.error(f"❌ Ошибка генерации концепций: {str(e)}")
        import traceback
        st.error(f"Детали ошибки: {traceback.format_exc()}")

def batch_processing_interface():
    """Интерфейс для пакетной обработки изображений"""
    
    from PIL import Image
    
    # Показываем существующие результаты, если они есть (но не при пересоздании)
    if "batch_results" in st.session_state and "batch_regenerate_params" not in st.session_state:
        st.markdown("---")
        st.subheader("🎨 Текущие результаты коллекции")
        
        # Кнопка очистки результатов
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Очистить результаты", type="secondary", use_container_width=True, help="Удалить все результаты и начать заново"):
                # Очищаем результаты из session_state
                if "batch_results" in st.session_state:
                    del st.session_state.batch_results
                if "batch_product_images" in st.session_state:
                    del st.session_state.batch_product_images
                if "batch_logo_image" in st.session_state:
                    del st.session_state.batch_logo_image
                st.rerun()
        
        batch_result = {
            "results": st.session_state.batch_results,
            "saved_paths": []  # Пустой список для существующих результатов
        }
        display_batch_results(batch_result)
        st.markdown("---")
    
    # Обработка пересоздания для пакетной обработки
    if "batch_regenerate_params" in st.session_state:
        regenerate_params = st.session_state.batch_regenerate_params
        item_index = regenerate_params["item_index"]
        
        st.info(f"🔄 Пересоздание товара: Товар {item_index + 1}")
        
        with st.spinner("Пересоздание товара с теми же параметрами..."):
            try:
                generator = get_mockup_generator()
                
                # Получаем параметры из оригинального промпта
                prompt_data = regenerate_params["prompt_data"]
                original_image = regenerate_params["original_image"]
                
                # Отладочная информация
                st.write(f"🔄 Пересоздание товара 'Товар {item_index + 1}' (индекс: {item_index})")
                st.write(f"📝 Промпт: {prompt_data.get('style', 'N/A')} стиль, {prompt_data.get('logo_application', 'N/A')} нанесение")
                
                # Генерируем новый мокап с теми же параметрами
                pattern_image = st.session_state.get("batch_pattern_image", None)
                new_result = generator.gemini_client.generate_mockup_with_analysis(
                    original_image, st.session_state.batch_logo_image, prompt_data, "", pattern_image
                )
                
                if new_result and len(new_result) > 0:
                    mockup = new_result[0]
                    st.write(f"✅ Получен новый мокап размером {len(mockup.get('image_data', b''))} байт")
                    
                    # Заменяем конкретный товар в результатах пакетной обработки
                    if "batch_results" in st.session_state:
                        batch_results = st.session_state.batch_results
                        st.write(f"📊 Найдено {len(batch_results)} товаров в результатах")
                        if item_index < len(batch_results):
                            # Обновляем мокап в результатах
                            batch_results[item_index]["mockup"] = mockup
                            batch_results[item_index]["status"] = "success"
                            # Обновляем session_state
                            st.session_state.batch_results = batch_results
                            st.success(f"✅ Товар {item_index + 1} пересоздан!")
                        else:
                            st.error(f"❌ Индекс товара {item_index} не найден в результатах (всего: {len(batch_results)})")
                    else:
                        st.error("❌ Результаты пакетной обработки не найдены в session_state")
                else:
                    st.error("❌ Не удалось пересоздать товар - пустой результат от Gemini")
                    st.write(f"Результат: {new_result}")
                
                # Очищаем параметры пересоздания
                del st.session_state.batch_regenerate_params
                
            except Exception as e:
                st.error(f"❌ Ошибка пересоздания: {e}")
                del st.session_state.batch_regenerate_params
        
        # Показываем обновленные результаты пакетной обработки
        if "batch_results" in st.session_state:
            # Создаем объект batch_result для display_batch_results
            batch_result = {
                "results": st.session_state.batch_results,
                "saved_paths": []  # Пустой список, так как мы не сохраняем файлы при пересоздании
            }
            display_batch_results(batch_result)
        return
    
    st.subheader("Пакетная обработка коллекции")
    st.markdown("Загрузите до 10 фотографий товаров для создания единой коллекции")
    
    # Верстка в 3 столбика как в одиночной обработке
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Блок загрузки товаров
        st.markdown('<div class="settings-block batch-products-block" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">', unsafe_allow_html=True)
        st.markdown("### Товары для коллекции")
        st.markdown("Загрузите до 10 фотографий товаров")
        
        product_files = st.file_uploader(
            "Загрузите изображения товаров",
            type=['jpg', 'jpeg', 'png', 'webp'],
            accept_multiple_files=True,
            key="batch_products"
        )
        
        if product_files and len(product_files) > 10:
            st.error("⚠️ Максимум 10 товаров за раз")
            product_files = product_files[:10]
        
        if product_files:
            # Конвертируем все изображения в RGB для совместимости с JPEG
            from image_processor import ImageProcessor
            processor = ImageProcessor()
            converted_images = []
            for f in product_files:
                img = Image.open(f)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = processor.convert_to_rgb(img)
                converted_images.append(img)
            st.session_state.batch_product_images = converted_images
            
            # Показываем превью товаров
            st.markdown(f"**Загружено товаров: {len(product_files)}**")
            
            # Показываем товары в сетке
            cols = st.columns(2)  # 2 колонки для превью
            for i, img in enumerate(st.session_state.batch_product_images):
                with cols[i % 2]:
                    preview_size = (60, 60)
                    preview_img = img.copy()
                    preview_img.thumbnail(preview_size, Image.LANCZOS)
                    st.image(preview_img, caption=f"Товар {i+1}", width=60)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Блок загрузки логотипа
        st.markdown('<div class="settings-block batch-logo-block" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">', unsafe_allow_html=True)
        st.markdown("### Логотип для коллекции")
        
        logo_file = st.file_uploader(
            "Загрузите логотип клиента",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="batch_logo"
        )
        
        if logo_file:
            logo_image = Image.open(logo_file)
            # Конвертируем в RGB для совместимости с JPEG
            if logo_image.mode in ('RGBA', 'LA', 'P'):
                from image_processor import ImageProcessor
                processor = ImageProcessor()
                logo_image = processor.convert_to_rgb(logo_image)
            st.session_state.batch_logo_image = logo_image
            
            # Компактное превью логотипа
            preview_size = (80, 80)
            preview_logo = logo_image.copy()
            preview_logo.thumbnail(preview_size, Image.LANCZOS)
            st.image(preview_logo, caption="Логотип", width=80)
            st.caption(f"{logo_image.size[0]}x{logo_image.size[1]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Блок дополнительных настроек
        st.markdown('<div class="settings-block batch-additional-block" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">', unsafe_allow_html=True)
        st.markdown("### Дополнительно")
        
        # Паттерн (опционально)
        pattern_file = st.file_uploader(
            "Паттерн (опционально)",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="batch_pattern",
            help="Паттерн будет использован для всех товаров коллекции"
        )
        
        if pattern_file:
            pattern_image = Image.open(pattern_file)
            # Конвертируем в RGB для совместимости с JPEG
            if pattern_image.mode in ('RGBA', 'LA', 'P'):
                from image_processor import ImageProcessor
                processor = ImageProcessor()
                pattern_image = processor.convert_to_rgb(pattern_image)
            st.session_state.batch_pattern_image = pattern_image
            
            # Компактное превью паттерна
            preview_size = (60, 60)
            preview_pattern = pattern_image.copy()
            preview_pattern.thumbnail(preview_size, Image.LANCZOS)
            st.image(preview_pattern, caption="Паттерн", width=60)
            st.caption(f"{pattern_image.size[0]}x{pattern_image.size[1]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Настройки коллекции
    if product_files and logo_file:
        st.markdown("---")
        st.markdown("**⚙️ Настройки коллекции**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Основные настройки с правильным дизайном
            st.markdown('<div class="settings-block batch-settings-block" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">', unsafe_allow_html=True)
            st.markdown("### Настройки коллекции")
            
            product_color = st.selectbox(
                "Цвет товаров",
                ["как на фото", "белый", "черный", "серый", "красный", "синий", "зеленый", "желтый", "розовый", "фиолетовый", "коричневый", "бежевый", "натуральный"],
                help="Основной цвет для всех товаров коллекции"
            )
            
            collection_style = st.selectbox(
                "Стиль коллекции",
                ["Современный", "Премиальный", "Минималистичный", "В динамике"],
                help="Единый стиль для всей коллекции"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Дополнительные настройки с правильным дизайном
            st.markdown('<div class="settings-block batch-additional-block" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">', unsafe_allow_html=True)
            st.markdown("### 4. Дополнительно")
            
            # Дополнительное описание для промптов
            custom_description = st.text_area(
                "Доп описание",
                placeholder="Дополнительные детали для всех товаров коллекции. Например: 'добавить тени', 'яркое освещение', 'премиум качество'",
                height=80,
                help="Дополнительные детали, которые будут добавлены к промптам всех товаров"
            )
            
            # Дополнительные опции
            add_tag = st.checkbox("Добавить бирки", value=False, help="Добавить этикетки или бирки с логотипом к товарам")
            add_person = st.checkbox("Показать в использовании", value=False, help="Показать товары в использовании")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Кнопка обработки
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Создать коллекцию", type="primary", use_container_width=True):
                with st.spinner("Анализ коллекции и создание промптов..."):
                    try:
                        batch_processor = get_batch_processor()
                        
                        # Анализ коллекции (AI определит нанесение, стиль задан)
                        analysis_result = batch_processor.analyze_collection(
                            product_images=st.session_state.batch_product_images,
                            logo_image=st.session_state.batch_logo_image,
                            product_color=product_color,
                            collection_style=collection_style
                        )
                        
                        if analysis_result["status"] == "success":
                            st.success("✅ Анализ коллекции завершен - AI проанализировал конкретные товары и определил оптимальное нанесение логотипа")
                            st.info("🔍 AI определил тип каждого товара и выбрал реалистичное нанесение логотипа для каждого")
                            
                            # Показываем настройки коллекции
                            if custom_description.strip() or add_tag or add_person:
                                with st.expander("⚙️ Настройки коллекции"):
                                    st.write(f"**Цвет товаров:** {product_color}")
                                    st.write(f"**Стиль коллекции:** {collection_style}")
                                    if custom_description.strip():
                                        st.write(f"**Дополнительное описание:** {custom_description}")
                                    if add_tag:
                                        st.write("**Дополнительно:** Добавлены бирки к товарам")
                                    if add_person:
                                        st.write("**Дополнительно:** Показать товары в использовании")
                            
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
                                    if prompt_data.get('custom_prompt'):
                                        st.write(f"- Дополнительно: {prompt_data['custom_prompt']}")
                                    st.markdown("---")
                            
                            # Обработка коллекции с прогресс-баром
                            st.info("🚀 Генерация мокапов коллекции...")
                            
                            # Создаем прогресс-бар
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            collection_settings = {
                                "product_color": product_color,
                                "collection_style": collection_style
                            }
                            
                            # Добавляем дополнительные опции к промптам
                            for prompt_data in analysis_result["individual_prompts"]:
                                extended_prompt = prompt_data.get("custom_prompt", "")
                                
                                # Добавляем логику для удаления фоновых объектов при смене ракурса
                                product_angle = prompt_data.get("product_angle", "как на фото")
                                if product_angle != "как на фото":
                                    extended_prompt += " Удалить все фоновые объекты, людей, мебель и окружение. Оставить только основной товар/товары на чистом фоне."
                                
                                # Добавляем дополнительное описание, если оно указано
                                if custom_description.strip():
                                    extended_prompt += f" {custom_description.strip()}"
                                
                                if add_tag:
                                    extended_prompt += " Добавить этикетку или бирку с логотипом к товару. Этикетка должна содержать логотип, который был загружен пользователем."
                                if add_person:
                                    extended_prompt += " Показать товар в использовании человеком."
                                
                                prompt_data["custom_prompt"] = extended_prompt
                            
                            # Обрабатываем каждый товар с обновлением прогресса
                            total_items = len(st.session_state.batch_product_images)
                            results = []
                            
                            for i, (product_img, prompt_data) in enumerate(zip(
                                st.session_state.batch_product_images,
                                analysis_result["individual_prompts"]
                            )):
                                # Обновляем прогресс
                                progress = (i + 1) / total_items
                                progress_bar.progress(progress)
                                status_text.text(f"Обработка {i+1}/{total_items}: Товар {i+1}")
                                
                                # Генерируем мокап для текущего товара
                                try:
                                    generator = get_mockup_generator()
                                    pattern_image = st.session_state.get("batch_pattern_image", None)
                                    mockup_result = generator.gemini_client.generate_mockup_with_analysis(
                                        product_img, st.session_state.batch_logo_image, prompt_data, "", pattern_image
                                    )
                                    
                                    if mockup_result and len(mockup_result) > 0:
                                        results.append({
                                            "index": i,
                                            "product_name": f"Товар {i+1}",
                                            "original_image": product_img,
                                            "mockup": mockup_result[0],
                                            "prompt_data": prompt_data,
                                            "status": "success"
                                        })
                                    else:
                                        results.append({
                                            "index": i,
                                            "product_name": f"Товар {i+1}",
                                            "original_image": product_img,
                                            "mockup": None,
                                            "prompt_data": prompt_data,
                                            "status": "error",
                                            "error": "Не удалось сгенерировать мокап"
                                        })
                                except Exception as e:
                                    results.append({
                                        "index": i,
                                        "product_name": f"Товар {i+1}",
                                        "original_image": product_img,
                                        "mockup": None,
                                        "prompt_data": prompt_data,
                                        "status": "error",
                                        "error": str(e)
                                    })
                            
                            # Создаем результат в формате batch_processor
                            successful = sum(1 for r in results if r["status"] == "success")
                            batch_result = {
                                "status": "success" if successful > 0 else "error",
                                "results": results,
                                "successful": successful,
                                "total_processed": total_items,
                                "processing_time": 0  # Время не отслеживается в этом подходе
                            }
                            
                            if batch_result["status"] == "success":
                                st.success(f"✅ Коллекция создана! Обработано {batch_result['successful']}/{batch_result['total_processed']} товаров")
                                # Сохраняем результаты в session_state для возможности пересоздания
                                st.session_state.batch_results = batch_result["results"]
                                display_batch_results(batch_result)
                            else:
                                st.error(f"❌ Ошибка обработки: {batch_result.get('error', 'Неизвестная ошибка')}")
                        
                        elif analysis_result["status"] == "fallback":
                            st.warning("⚠️ Использованы базовые промпты (AI анализ недоступен)")
                            
                            # Обработка с базовыми промптами и прогресс-баром
                            st.info("🚀 Генерация мокапов с базовыми промптами...")
                            
                            # Создаем прогресс-бар
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            collection_settings = {
                                "product_color": product_color,
                                "collection_style": collection_style
                            }
                            
                            # Добавляем дополнительные опции к промптам (fallback случай)
                            for prompt_data in analysis_result["individual_prompts"]:
                                extended_prompt = prompt_data.get("custom_prompt", "")
                                
                                # Добавляем логику для удаления фоновых объектов при смене ракурса
                                product_angle = prompt_data.get("product_angle", "как на фото")
                                if product_angle != "как на фото":
                                    extended_prompt += " Удалить все фоновые объекты, людей, мебель и окружение. Оставить только основной товар/товары на чистом фоне."
                                
                                # Добавляем дополнительное описание, если оно указано
                                if custom_description.strip():
                                    extended_prompt += f" {custom_description.strip()}"
                                
                                if add_tag:
                                    extended_prompt += " Добавить этикетку или бирку с логотипом к товару. Этикетка должна содержать логотип, который был загружен пользователем."
                                if add_person:
                                    extended_prompt += " Показать товар в использовании человеком."
                                
                                prompt_data["custom_prompt"] = extended_prompt
                            
                            # Обрабатываем каждый товар с обновлением прогресса
                            total_items = len(st.session_state.batch_product_images)
                            results = []
                            
                            for i, (product_img, prompt_data) in enumerate(zip(
                                st.session_state.batch_product_images,
                                analysis_result["individual_prompts"]
                            )):
                                # Обновляем прогресс
                                progress = (i + 1) / total_items
                                progress_bar.progress(progress)
                                status_text.text(f"Обработка {i+1}/{total_items}: Товар {i+1}")
                                
                                # Генерируем мокап для текущего товара
                                try:
                                    generator = get_mockup_generator()
                                    pattern_image = st.session_state.get("batch_pattern_image", None)
                                    mockup_result = generator.gemini_client.generate_mockup_with_analysis(
                                        product_img, st.session_state.batch_logo_image, prompt_data, "", pattern_image
                                    )
                                    
                                    if mockup_result and len(mockup_result) > 0:
                                        results.append({
                                            "index": i,
                                            "product_name": f"Товар {i+1}",
                                            "original_image": product_img,
                                            "mockup": mockup_result[0],
                                            "prompt_data": prompt_data,
                                            "status": "success"
                                        })
                                    else:
                                        results.append({
                                            "index": i,
                                            "product_name": f"Товар {i+1}",
                                            "original_image": product_img,
                                            "mockup": None,
                                            "prompt_data": prompt_data,
                                            "status": "error",
                                            "error": "Не удалось сгенерировать мокап"
                                        })
                                except Exception as e:
                                    results.append({
                                        "index": i,
                                        "product_name": f"Товар {i+1}",
                                        "original_image": product_img,
                                        "mockup": None,
                                        "prompt_data": prompt_data,
                                        "status": "error",
                                        "error": str(e)
                                    })
                            
                            # Создаем результат в формате batch_processor
                            successful = sum(1 for r in results if r["status"] == "success")
                            batch_result = {
                                "status": "success" if successful > 0 else "error",
                                "results": results,
                                "successful": successful,
                                "total_processed": total_items,
                                "processing_time": 0  # Время не отслеживается в этом подходе
                            }
                            
                            if batch_result["status"] == "success":
                                st.success(f"✅ Коллекция создана! Обработано {batch_result['successful']}/{batch_result['total_processed']} товаров")
                                # Сохраняем результаты в session_state для возможности пересоздания
                                st.session_state.batch_results = batch_result["results"]
                                display_batch_results(batch_result)
                            else:
                                st.error(f"❌ Ошибка обработки: {batch_result.get('error', 'Неизвестная ошибка')}")
                        
                        else:
                            st.error(f"❌ Ошибка анализа коллекции: {analysis_result.get('error', 'Неизвестная ошибка')}")
                    
                    except Exception as e:
                        st.error(f"❌ Критическая ошибка: {e}")
                        st.error("Попробуйте перезагрузить страницу или проверить изображения")
    
    else:
        st.info("👆 Загрузите логотип и товары для создания коллекции")

def display_batch_results(batch_result: dict):
    """Отображение результатов пакетной обработки"""
    
    results = batch_result.get("results", [])
    
    if not results:
        st.error("❌ Нет результатов для отображения")
        return
    
    st.markdown("---")
    st.subheader("🎨 Результаты коллекции")
    
    # Группируем результаты по строкам
    for i in range(0, len(results), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(results):
                result = results[i + j]
                
                with col:
                    if result["status"] == "success" and result["mockup"]:
                        product_name = result.get("product_name", f"Товар {result['index'] + 1}")
                        st.markdown(f"**{product_name}**")
                        
                        # Отображение мокапа
                        if "image_data" in result["mockup"]:
                            try:
                                from PIL import Image
                                import io
                                from image_processor import ImageProcessor
                                
                                image_data = result["mockup"]["image_data"]
                                image = Image.open(io.BytesIO(image_data))
                                
                                # Конвертируем в RGB для совместимости с JPEG
                                if image.mode in ('RGBA', 'LA', 'P'):
                                    processor = ImageProcessor()
                                    image = processor.convert_to_rgb(image)
                                    # Обновляем image_data
                                    img_byte_arr = io.BytesIO()
                                    image.save(img_byte_arr, format='JPEG', quality=95)
                                    image_data = img_byte_arr.getvalue()
                                
                                st.image(image, use_container_width=True)
                                
                                # Кнопки управления
                                col_download, col_regenerate = st.columns(2)
                                
                                with col_download:
                                    # Кнопка скачивания
                                    st.download_button(
                                        label=f"📥 Скачать",
                                        data=image_data,
                                        file_name=f"collection_item_{result['index'] + 1}.jpg",
                                        mime="image/jpeg",
                                        key=f"download_batch_{result['index']}",
                                        use_container_width=True
                                    )
                                    
                                    # Загружаем на FTP
                                    try:
                                        from services.upload_services import upload_to_ftp
                                        upload_to_ftp(
                                            image_data=image_data,
                                            metadata={
                                                'product_name': product_name,
                                                'generation_type': 'batch',
                                                'item_index': result['index'],
                                                'prompt_data': result.get("prompt_data", {})
                                            },
                                            description=f"Пакетная обработка: {product_name}"
                                        )
                                        # {product_name} загружен на FTP (без уведомления)
                                    except Exception as e:
                                        st.warning(f"⚠️ Не удалось загрузить {product_name} на FTP: {str(e)}")
                                
                                with col_regenerate:
                                    # Кнопка пересоздания
                                    if st.button(f"🎨 Перегенерировать", key=f"regenerate_batch_{result['index']}", use_container_width=True, help="Создать новый мокап с теми же параметрами"):
                                        # Сохраняем параметры для пересоздания
                                        st.session_state.batch_regenerate_params = {
                                            "item_index": result['index'],
                                            "product_name": f"Товар {i+1}",
                                            "prompt_data": result["prompt_data"],
                                            "original_image": result["original_image"]
                                        }
                                        st.rerun()
                            except Exception as e:
                                st.error(f"Ошибка отображения изображения: {e}")
                        
                        # Информация о промпте
                        with st.expander(f"📝 Промпт {product_name}"):
                            prompt_data = result["prompt_data"]
                            st.write(f"**Стиль:** {prompt_data.get('style', 'N/A')}")
                            st.write(f"**Нанесение:** {prompt_data.get('logo_application', 'N/A')}")
                            st.write(f"**Расположение:** {prompt_data.get('logo_position', 'N/A')}")
                            st.write(f"**Размер:** {prompt_data.get('logo_size', 'N/A')}")
                            st.write(f"**Цвет:** {prompt_data.get('logo_color', 'N/A')}")
                            if prompt_data.get('custom_prompt'):
                                st.write(f"**Дополнительно:** {prompt_data['custom_prompt']}")
                    
                    else:
                        product_name = result.get("product_name", f"Товар {result['index'] + 1}")
                        st.error(f"❌ Ошибка обработки {product_name}")
                        if result.get("error"):
                            st.write(f"Ошибка: {result['error']}")
    
    # Информация о сохранении
    if "saved_paths" in batch_result and batch_result["saved_paths"]:
        st.info(f"📁 Результаты сохранены: {len(batch_result['saved_paths'])} файлов")
        with st.expander("📁 Пути к файлам"):
            for i, path in enumerate(batch_result["saved_paths"]):
                st.write(f"{i+1}. {path}")


def upload_to_google_drive(image_data: bytes, metadata: dict, description: str = ""):
    """Google Drive отключен"""
    pass

def get_google_drive_mockups(limit: int = 50) -> list:
    """Google Drive отключен"""
    return []

def get_all_mockups_data():
    """Получает все мокапы из разных источников"""
    all_mockups_data = []
    
    # Проверяем session_state на наличие изображений (временно отключено)
    session_mockups = []
    # if "generated_mockups" in st.session_state:
    #     for i, mockup_data in enumerate(st.session_state.generated_mockups):
    #         if "image_data" in mockup_data:
    #             session_mockups.append({
    #                 'image_file': f"session_mockup_{i+1}.jpg",
    #                 'image_path': f"session_state_{i}",
    #                 'cache_key': f"session_{i}",
    #                 'metadata': mockup_data.get('metadata', {}),
    #                 'created_time': mockup_data.get('timestamp', time.time()),
    #                 'source': 'session_state',
    #                 'image_data': mockup_data['image_data']
    #             })
    
    # Google Drive отключен
    drive_mockups = []
    
    # Получаем мокапы с сервера
    server_mockups = get_server_mockups(50)
    
    # Получаем мокапы с FTP
    ftp_mockups = get_ftp_mockups(50)
    
    # Объединяем только FTP мокапы (остальные временно отключены)
    all_mockups_data.extend(ftp_mockups)
    
    if not all_mockups_data:
        st.info("📁 Галерея пока пуста. Сгенерируйте несколько мокапов, чтобы увидеть их здесь!")
        
        storage_info = []
        if SERVER_STORAGE_ENABLED:
            storage_info.append("серверное хранилище")
        if FTP_ENABLED:
            storage_info.append("FTP сервер")
        storage_info.append("память сессии")
        
        if storage_info:
            st.info(f"💡 Изображения сохраняются в: {', '.join(storage_info)}")
        
        # Отладочная информация
        with st.expander("🔍 Отладочная информация"):
            st.write(f"**Текущая рабочая директория:** {os.getcwd()}")
            st.write(f"**Проверяемые папки:**")
            st.write(f"- `{outputs_dir}`: {'✅ существует' if os.path.exists(outputs_dir) else '❌ не существует'}")
            # Определяем cache_images_dir для отладки
            cache_images_dir = os.path.join(cache_dir, "images")
            st.write(f"- `{cache_images_dir}`: {'✅ существует' if os.path.exists(cache_images_dir) else '❌ не существует'}")
            
            if os.path.exists(outputs_dir):
                files = os.listdir(outputs_dir)
                st.write(f"**Файлы в {outputs_dir}:** {files}")
            
            if os.path.exists(cache_images_dir):
                files = os.listdir(cache_images_dir)
                st.write(f"**Файлы в {cache_images_dir}:** {files}")
            
            st.write(f"**Мокапы в session_state:** {len(session_mockups)}")
            st.write(f"**Google Drive отключен**")
        
        return
    
    mockups_data = all_mockups_data
    
    # Сортируем по дате создания (новые сверху)
    mockups_data.sort(key=lambda x: x['created_time'], reverse=True)
    
    # Фильтры
    st.markdown("### 🔍 Фильтры")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Фильтр по стилю
        all_styles = set()
        for mockup in mockups_data:
            style = mockup['metadata'].get('mockup_style', 'Неизвестно')
            all_styles.add(style)
        
        selected_style = st.selectbox(
            "Стиль мокапа:",
            ["Все"] + sorted(list(all_styles)),
            index=0
        )
    
    with col2:
        # Фильтр по типу нанесения
        all_applications = set()
        for mockup in mockups_data:
            application = mockup['metadata'].get('logo_application', 'Неизвестно')
            all_applications.add(application)
        
        selected_application = st.selectbox(
            "Тип нанесения:",
            ["Все"] + sorted(list(all_applications)),
            index=0
        )
    
    with col3:
        # Фильтр по дате
        date_filter = st.selectbox(
            "Период:",
            ["Все", "Сегодня", "За неделю", "За месяц"],
            index=0
        )
    
    # Применяем фильтры
    filtered_mockups = mockups_data
    
    if selected_style != "Все":
        filtered_mockups = [m for m in filtered_mockups if m['metadata'].get('mockup_style') == selected_style]
    
    if selected_application != "Все":
        filtered_mockups = [m for m in filtered_mockups if m['metadata'].get('logo_application') == selected_application]
    
    if date_filter != "Все":
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if date_filter == "Сегодня":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "За неделю":
            cutoff = now - timedelta(days=7)
        elif date_filter == "За месяц":
            cutoff = now - timedelta(days=30)
        
        filtered_mockups = [m for m in filtered_mockups if datetime.fromtimestamp(m['created_time']) >= cutoff]
    
    # Показываем количество найденных результатов
    st.markdown(f"### 📊 Найдено мокапов: {len(filtered_mockups)}")
    
    if not filtered_mockups:
        st.info("🔍 По выбранным фильтрам мокапы не найдены")
        return
    
    # Отображаем мокапы в виде плиток
    st.markdown("### 🖼️ Мокапы")
    
    # Настройки отображения
    col1, col2 = st.columns([3, 1])
    with col2:
        images_per_row = st.selectbox("Изображений в ряду:", [2, 3, 4], index=1)
    
    # Создаем сетку изображений
    for i in range(0, len(filtered_mockups), images_per_row):
        cols = st.columns(images_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(filtered_mockups):
                mockup = filtered_mockups[i + j]
                
                with col:
                    # Отображаем изображение с улучшенной обработкой ошибок
                    try:
                        image = None
                        file_size = 0
                        
                        # Обрабатываем изображения из session_state
                        if mockup.get('source') == 'session_state' and 'image_data' in mockup:
                            try:
                                import base64
                                import io
                                image_data = base64.b64decode(mockup['image_data'])
                                image = Image.open(io.BytesIO(image_data))
                                file_size = len(image_data)
                                st.image(image, use_container_width=True, caption=f"Мокап {i + j + 1} (из сессии)")
                            except Exception as session_error:
                                st.error(f"❌ Ошибка загрузки изображения из сессии: {str(session_error)}")
                                continue
                        
                        # Обрабатываем файловые изображения
                        else:
                            # Для FTP мокапов используем web_url
                            if mockup.get('source') == 'ftp_upload' and 'web_url' in mockup:
                                try:
                                    import requests
                                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                                    response = requests.get(mockup['web_url'], timeout=10, headers=headers)
                                    if response.status_code == 200:
                                        image = Image.open(io.BytesIO(response.content))
                                        st.image(image, use_container_width=True, caption=f"Мокап {i + j + 1} (с сервера)")
                                        file_size = len(response.content)
                                    else:
                                        # Скрываем недоступные файлы вместо показа ошибки
                                        print(f"⚠️ Файл недоступен: {mockup['web_url']} (HTTP {response.status_code})")
                                        continue
                                except Exception as web_error:
                                    # Скрываем файлы с ошибками вместо показа ошибки
                                    print(f"⚠️ Ошибка загрузки: {mockup['web_url']} - {str(web_error)}")
                                    continue
                            
                            # Для локальных файлов
                            else:
                                # Проверяем существование файла
                                if not os.path.exists(mockup['image_path']):
                                    st.warning(f"⚠️ Файл не найден: {mockup['image_file']}")
                                    st.write(f"**Путь:** {mockup['image_path']}")
                                    st.write(f"**Источник:** {mockup.get('source', 'неизвестно')}")
                                    continue
                                
                                # Проверяем размер файла
                                file_size = os.path.getsize(mockup['image_path'])
                                if file_size == 0:
                                    st.warning(f"⚠️ Файл пустой: {mockup['image_file']}")
                                    continue
                                
                                # Пытаемся открыть изображение
                                try:
                                    image = Image.open(mockup['image_path'])
                                    # Проверяем, что это действительно изображение
                                    image.verify()
                                    
                                    # Если все хорошо, открываем заново для отображения
                                    image = Image.open(mockup['image_path'])
                                    st.image(image, use_container_width=True, caption=f"Мокап {i + j + 1}")
                                    
                                except Exception as img_error:
                                    st.error(f"❌ Поврежденный файл изображения: {mockup['image_file']}")
                                    st.write(f"**Ошибка:** {str(img_error)}")
                                    st.write(f"**Размер файла:** {file_size} байт")
                                    st.write(f"**Путь:** {mockup['image_path']}")
                                    
                                    # Показываем метаданные даже для поврежденных файлов
                                    with st.expander(f"ℹ️ Детали мокапа {i + j + 1} (файл поврежден)"):
                                        metadata = mockup['metadata']
                                        
                                        # Основная информация
                                        st.write("**Основные параметры:**")
                                        st.write(f"• Стиль: {metadata.get('mockup_style', 'Неизвестно')}")
                                        st.write(f"• Тип нанесения: {metadata.get('logo_application', 'Неизвестно')}")
                                        st.write(f"• Расположение логотипа: {metadata.get('logo_placement', 'Неизвестно')}")
                                        st.write(f"• Размер логотипа: {metadata.get('logo_size', 'Неизвестно')}")
                                        
                                        # Дополнительная информация
                                        if metadata.get('special_requirements'):
                                            st.write(f"**Особые требования:** {metadata['special_requirements']}")
                                        
                                        # Время создания
                                        created_time = datetime.fromtimestamp(mockup['created_time'])
                                        st.write(f"**Создан:** {created_time.strftime('%d.%m.%Y %H:%M')}")
                                        
                                        st.warning("⚠️ Файл изображения поврежден и не может быть отображен")
                                    continue
                        
                        # Метаданные в expander для корректных изображений
                        with st.expander(f"ℹ️ Детали мокапа {i + j + 1}"):
                            metadata = mockup['metadata']
                            
                            # Основная информация
                            st.write("**Основные параметры:**")
                            st.write(f"• Стиль: {metadata.get('mockup_style', 'Неизвестно')}")
                            st.write(f"• Тип нанесения: {metadata.get('logo_application', 'Неизвестно')}")
                            st.write(f"• Расположение логотипа: {metadata.get('logo_placement', 'Неизвестно')}")
                            st.write(f"• Размер логотипа: {metadata.get('logo_size', 'Неизвестно')}")
                            
                            # Дополнительная информация
                            if metadata.get('special_requirements'):
                                st.write(f"**Особые требования:** {metadata['special_requirements']}")
                            
                            # Время создания
                            created_time = datetime.fromtimestamp(mockup['created_time'])
                            st.write(f"**Создан:** {created_time.strftime('%d.%m.%Y %H:%M')}")
                            
                            # Информация о файле
                            st.write(f"**Файл:** {mockup['image_file']}")
                            st.write(f"**Размер:** {file_size} байт")
                            st.write(f"**Источник:** {mockup.get('source', 'неизвестно')}")
                            
                            # Кнопка скачивания
                            try:
                                if mockup.get('source') == 'session_state' and 'image_data' in mockup:
                                    # Скачивание из session_state
                                    import base64
                                    image_data = base64.b64decode(mockup['image_data'])
                                    st.download_button(
                                        label="📥 Скачать",
                                        data=image_data,
                                        file_name=mockup['image_file'],
                                        mime="image/jpeg"
                                    )
                                else:
                                    # Скачивание из файла
                                    with open(mockup['image_path'], "rb") as file:
                                        st.download_button(
                                            label="📥 Скачать",
                                            data=file.read(),
                                            file_name=mockup['image_file'],
                                            mime="image/jpeg"
                                        )
                            except Exception as download_error:
                                st.error(f"Ошибка скачивания: {str(download_error)}")
                    
                    except Exception as e:
                        st.error(f"❌ Критическая ошибка: {str(e)}")
                        st.write(f"**Файл:** {mockup['image_file']}")
                        st.write(f"**Путь:** {mockup['image_path']}")
    
    # Статистика внизу
    st.markdown("---")
    st.markdown("### 📈 Статистика")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Всего мокапов", len(mockups_data))
    
    with col2:
        st.metric("Отфильтровано", len(filtered_mockups))
    
    with col3:
        if mockups_data:
            latest = max(mockups_data, key=lambda x: x['created_time'])
            latest_time = datetime.fromtimestamp(latest['created_time'])
            st.metric("Последний мокап", latest_time.strftime('%d.%m.%Y'))
    
    with col4:
        # Размер папки с изображениями
        total_size = 0
        for mockup in mockups_data:
            try:
                total_size += os.path.getsize(mockup['image_path'])
            except:
                pass
        
        st.metric("Размер папки", f"{total_size / (1024*1024):.1f} МБ")

def upload_to_google_drive(image_data: bytes, metadata: dict, description: str = ""):
    """Google Drive отключен"""
    pass

def get_google_drive_mockups(limit: int = 50) -> list:
    """Google Drive отключен"""
    return []

def upload_to_server(image_data: bytes, metadata: dict, description: str = ""):
    """Загружает мокап на сервер"""
    if not SERVER_STORAGE_ENABLED:
        return
    
    try:
        from server_storage import get_server_storage
        
        # Получаем хранилище сервера
        storage = get_server_storage()
        
        # Загружаем файл
        filename = storage.save_mockup(image_data, metadata, description)
        if filename:
            print(f"✅ Мокап загружен на сервер: {filename}")
        else:
            print(f"❌ Ошибка загрузки на сервер")
            
    except Exception as e:
        print(f"❌ Ошибка загрузки на сервер: {e}")

def get_server_mockups(limit: int = 50) -> list:
    """Получает список мокапов с сервера"""
    if not SERVER_STORAGE_ENABLED:
        return []
    
    try:
        from server_storage import get_server_storage
        
        # Получаем хранилище сервера
        storage = get_server_storage()
        
        # Получаем список мокапов
        mockups = storage.get_mockups_list(limit)
        
        # Преобразуем в формат для галереи
        gallery_mockups = []
        for mockup in mockups:
            gallery_mockups.append({
                'image_file': mockup['filename'],
                'image_path': mockup['filepath'],
                'cache_key': mockup['id'],
                'metadata': mockup['metadata'],
                'created_time': mockup['created_time'],
                'source': 'server_storage',
                'image_data': mockup.get('image_data'),
                'web_url': mockup.get('web_url')
            })
        
        return gallery_mockups
        
    except Exception as e:
        print(f"❌ Ошибка получения мокапов с сервера: {e}")
        return []

def upload_to_ftp(image_data: bytes, metadata: dict, description: str = ""):
    """Загружает мокап на FTP сервер с сжатием"""
    if not FTP_ENABLED:
        return
    
    try:
        from ftp_uploader import get_ftp_uploader
        from image_processor import ImageProcessor
        
        # Получаем FTP загрузчик
        uploader = get_ftp_uploader()
        if not uploader:
            return
        
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
        # Сжатие и загрузка на FTP (без уведомлений)
        filename = uploader.upload_mockup(compressed_data, metadata, description)
            
    except Exception as e:
        print(f"❌ Ошибка загрузки на FTP: {e}")

def get_ftp_mockups(limit: int = 50) -> list:
    """Получает список мокапов с FTP сервера"""
    if not FTP_ENABLED:
        return []
    
    try:
        from ftp_uploader import get_ftp_uploader
        import requests
        
        # Получаем FTP загрузчик
        uploader = get_ftp_uploader()
        if not uploader:
            return []
        
        # Получаем список мокапов
        mockups = uploader.list_files()
        
        # Преобразуем в формат для галереи и проверяем веб-доступ
        gallery_mockups = []
        for mockup in mockups[:limit]:
            # Проверяем, что файл доступен через веб
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.head(mockup['web_url'], timeout=5, headers=headers)
                if response.status_code == 200:
                    gallery_mockups.append({
                        'image_file': mockup['filename'],
                        'image_path': mockup['web_url'],
                        'cache_key': mockup['filename'].replace('.jpg', ''),
                        'metadata': mockup['metadata'],
                        'created_time': time.time(),  # FTP не возвращает время создания
                        'source': 'ftp_upload',
                        'web_url': mockup['web_url']
                    })
                else:
                    print(f"⚠️ Файл недоступен через веб: {mockup['filename']} (HTTP {response.status_code})")
            except Exception as web_error:
                print(f"⚠️ Ошибка проверки веб-доступа для {mockup['filename']}: {web_error}")
                continue
        
        print(f"✅ Найдено рабочих FTP мокапов: {len(gallery_mockups)}")
        return gallery_mockups
        
    except Exception as e:
        print(f"❌ Ошибка получения мокапов с FTP: {e}")
        return []

def show_gallery_statistics(mockups: list):
    """Показывает статистику галереи"""
    st.markdown("### 📊 Статистика галереи")
    
    # Статистика по источникам
    sources = {}
    styles = {}
    applications = {}
    total_size = 0
    
    for mockup in mockups:
        source = mockup.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
        
        metadata = mockup.get('metadata', {})
        style = metadata.get('mockup_style', 'Неизвестно')
        application = metadata.get('logo_application', 'Неизвестно')
        
        styles[style] = styles.get(style, 0) + 1
        applications[application] = applications.get(application, 0) + 1
        
        # Размер файла (если доступен)
        if 'optimized_size' in metadata:
            total_size += metadata['optimized_size']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**По источникам:**")
        for source, count in sources.items():
            st.write(f"- {source}: {count}")
        
        st.markdown("**По стилям:**")
        for style, count in sorted(styles.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"- {style}: {count}")
    
    with col2:
        st.markdown("**По типам нанесения:**")
        for app, count in sorted(applications.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.write(f"- {app}: {count}")
        
        if total_size > 0:
            st.markdown("**Общий размер:**")
            st.write(f"- {total_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
