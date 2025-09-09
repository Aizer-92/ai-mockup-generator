"""
Веб-интерфейс для AI Mockup Generator
Использует Streamlit для простого и быстрого интерфейса
"""
import streamlit as st
import os
from PIL import Image
import time
from typing import Optional

# Импортируем конфигурацию после инициализации Streamlit
from config import get_config, STREAMLIT_PORT, STREAMLIT_HOST
from auth import is_authenticated, login_form, logout_button, require_auth
from mockup_generator import MockupGenerator
from batch_processor import BatchProcessor

# Получаем актуальную конфигурацию
config = get_config()

# Настройка страницы
st.set_page_config(
    page_title="AI Mockup Generator",
    page_icon="🎨",
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
    
    /* Фоновые блоки для настроек - красивый серый стиль */
    .settings-block {
        background: #f8f9fa !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 1px solid #e9ecef !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        transition: all 0.3s ease !important;
    }
    
    .settings-block:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.12) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Специальные блоки с серым фоном - более точечная стилизация */
    .product-block,
    .logo-block, 
    .additional-block,
    .batch-logo-block,
    .batch-pattern-block,
    .batch-products-block,
    .batch-settings-block,
    .batch-additional-block {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-left: 4px solid #6c757d !important;
    }
    
    /* Убираем цветные градиенты, делаем все блоки серыми */
    .product-block, .logo-block, .additional-block {
        background: #f8f9fa !important;
        border-left: 4px solid #6c757d !important;
    }
    
    /* Стили для заголовков блоков */
    .settings-block h3, .stContainer h3 {
        color: #495057 !important;
        margin-bottom: 1.5rem !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #e9ecef !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Мягкие кнопки режима */
    .stButton > button[kind="primary"] {
        background-color: #f8f9fa !important;
        color: #495057 !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 500;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #6c757d !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 400;
    }
    
    .stButton > button:hover {
        background-color: #e9ecef !important;
        border-color: #adb5bd !important;
        transform: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
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
    
    # Основной заголовок
    st.markdown("# AI Mockup Generator")
    st.markdown("Создавайте профессиональные мокапы товаров с логотипами клиентов")
    
    # Кнопка выхода в правом верхнем углу
    col1, col2 = st.columns([4, 1])
    with col2:
        logout_button()
    
    # Выбор режима работы с улучшенным дизайном
    st.markdown("---")
    st.markdown("### Режим работы")
    
    # Создаем кнопки-переключатели
    col1, col2 = st.columns(2)
    
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
    
    # Определяем режим
    mode = 'single' if st.session_state.get('mode', 'single') == 'single' else 'batch'
    
    # Показываем соответствующий интерфейс
    if mode == 'single':
        single_generation_interface()
    else:
        batch_processing_interface()

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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Блок "Товар" с красивым фоном
        with st.container():
            st.markdown('<div class="settings-block product-block">', unsafe_allow_html=True)
            st.markdown("### Товар")
            
            # Загрузка изображения товара
            product_file = st.file_uploader(
                "Загрузите товар",
                type=['jpg', 'jpeg', 'png', 'webp'],
                key="product"
            )
            
            if product_file:
                product_image = Image.open(product_file)
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
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Блок "Логотип" с красивым фоном
        with st.container():
            st.markdown('<div class="settings-block logo-block">', unsafe_allow_html=True)
            st.markdown("### Логотип")
            
            # Загрузка логотипа
            logo_file = st.file_uploader(
                "Загрузите логотип",
                type=['jpg', 'jpeg', 'png', 'webp'],
                key="logo"
            )
            
            if logo_file:
                logo_image = Image.open(logo_file)
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
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        # Блок "Дополнительно" с красивым фоном
        with st.container():
            st.markdown('<div class="settings-block additional-block">', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Компактные кнопки управления
    if ("product_image" in st.session_state and "logo_image" in st.session_state):
        st.markdown("---")
        
        # Компактные кнопки управления
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("Сгенерировать мокапы", type="primary", use_container_width=True):
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
                        
                        # Отладочная информация
                        print(f"Mockup style from UI: '{mockup_style}'")
                        print(f"Product color from UI: '{product_color}'")
                        print(f"Product angle from UI: '{product_angle}'")
                        print(f"Logo application from UI: '{custom_application.strip() if custom_application.strip() else logo_application}' -> '{logo_application_key}'")
                        print(f"Logo position from UI: '{logo_position}'")
                        print(f"Logo size from UI: '{logo_size}'")
                        print(f"Logo color from UI: '{logo_color}'")
                        print(f"Custom prompt from UI: '{custom_prompt}'")
                        print(f"Logo application type: {type(logo_application)}")
                        print(f"Logo application repr: {repr(logo_application)}")
                        
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
                        
                        # Показываем пользователю, что будет использовано
                        st.info(f"📦 Товар: {mockup_style} стиль, {product_color} цвет, {product_angle} ракурс")
                        st.info(f"🏷️ Логотип: {logo_application}, {logo_position}, {logo_size} размер, {logo_color} цвет")
                        
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
                            st.info(f"🔧 Дополнительно: {', '.join(additional_options)}")
                        
                        if custom_prompt.strip():
                            st.info(f"📝 Дополнительные требования: {custom_prompt}")
                        
                        # Показываем детальную информацию для отладки
                        with st.expander("🔍 Отладочная информация"):
                            st.write("**📦 Товар:**")
                            st.write(f"- Стиль: `{mockup_style}`")
                            st.write(f"- Цвет: `{product_color}`")
                            st.write(f"- Ракурс: `{product_angle}`")
                            st.write("**🏷️ Логотип:**")
                            st.write(f"- Тип нанесения: `{custom_application.strip() if custom_application.strip() else logo_application}` -> `{logo_application_key}`")
                            st.write(f"- Расположение: `{logo_position}`")
                            st.write(f"- Размер: `{logo_size}`")
                            st.write(f"- Цвет: `{logo_color}`")
                            st.write("**🔧 Дополнительные опции:**")
                            st.write(f"- Добавить бирку: `{add_tag if 'add_tag' in locals() else False}`")
                            st.write(f"- Добавить человека: `{add_person if 'add_person' in locals() else False}`")
                            st.write(f"- Добавить шильдик: `{add_badge if 'add_badge' in locals() else False}`")
                            if "pattern_image" in st.session_state:
                                st.write(f"- Паттерн загружен: `Да`")
                            else:
                                st.write(f"- Паттерн загружен: `Нет`")
                            st.write("**📝 Промпт:**")
                            st.write(f"- Исходные требования: `{custom_prompt}`")
                            st.write(f"- Расширенный промпт: `{extended_prompt}`")
                            st.write(f"- Длина промпта: {len(extended_prompt.strip()) if extended_prompt else 0}")
                            
                            # Показываем, какой эффект будет использоваться
                            material_adaptations = {
                                "fabric": {
                                    "embroidery": "embroidered with raised thread texture, realistic stitching details, and fabric-appropriate integration",
                                    "printing": "printed with smooth, flat surface, crisp edges, and fabric-appropriate ink absorption",
                                    "woven": "woven into the fabric with integrated texture, natural appearance, and seamless blending",
                                    "embossed": "embossed with raised relief effect, realistic depth, and fabric-appropriate texture",
                                    "sublimation": "sublimated with vibrant colors, smooth finish, and permanent integration into fabric",
                                    "vinyl": "vinyl heat transfer with glossy finish, crisp edges, and durable application",
                                    "heat_transfer": "heat transfer with smooth application, vibrant colors, and professional finish",
                                    "screen_print": "screen printed with thick ink, matte finish, and durable application",
                                    "digital_print": "digitally printed with high resolution, smooth finish, and precise details",
                                    "laser_engraving": "laser engraved with subtle texture, permanent marking, and professional appearance"
                                }
                            }
                            
                            product_type = "fabric"  # По умолчанию
                            material_dict = material_adaptations.get(product_type, material_adaptations["fabric"])
                            
                            if logo_application_key in material_dict:
                                logo_effect = material_dict[logo_application_key]
                                st.write(f"**Эффект логотипа:** `{logo_effect}`")
                            else:
                                # Используем первый доступный (не embroidery)
                                available_methods = [k for k in material_dict.keys() if k != "embroidery"]
                                if available_methods:
                                    fallback_method = available_methods[0]
                                    logo_effect = material_dict[fallback_method]
                                    st.warning(f"⚠️ Тип нанесения '{logo_application_key}' не найден, используется: '{fallback_method}'")
                                    st.write(f"**Эффект логотипа:** `{logo_effect}`")
                                else:
                                    st.error(f"❌ Тип нанесения '{logo_application_key}' не найден в словаре!")
                                    st.write(f"**Доступные типы:** {list(material_dict.keys())}")
                        
                        # Показываем, что именно отправляется в Gemini
                        st.info("🚀 Отправляем запрос в Gemini 2.5 Flash...")
                        st.write(f"**Параметры:**")
                        st.write(f"- Стиль: {mockup_style}")
                        st.write(f"- Тип нанесения: {logo_application}")
                        st.write(f"- Дополнительные требования: {custom_prompt if custom_prompt.strip() else 'Нет'}")
                        
                        # Показываем полный промпт для отладки
                        with st.expander("🔍 Полный промпт для Gemini (отладка)"):
                            # Создаем промпт как в gemini_client.py
                            style_descriptions = {
                                "modern": "Clean, minimalist design with sharp lines and contemporary aesthetics",
                                "vintage": "Classic, retro style with warm tones and traditional elements",
                                "minimal": "Ultra-clean design with maximum white space and simple elements",
                                "luxury": "Premium, high-end appearance with elegant details and rich materials",
                                "corporate": "Professional, business-oriented design with formal presentation"
                            }
                            
                            material_adaptations = {
                                "fabric": {
                                    "embroidery": "embroidered with raised thread texture",
                                    "printing": "printed with smooth, flat appearance",
                                    "woven": "woven into the fabric with integrated texture",
                                    "embossed": "embossed with raised surface details"
                                },
                                "textile": {
                                    "embroidery": "embroidered with raised thread texture",
                                    "printing": "printed with smooth, flat appearance",
                                    "woven": "woven into the textile with integrated texture",
                                    "embossed": "embossed with raised surface details"
                                },
                                "leather": {
                                    "embroidery": "embroidered with raised thread texture",
                                    "printing": "printed with smooth, flat appearance",
                                    "woven": "woven into the leather with integrated texture",
                                    "embossed": "embossed with raised surface details"
                                }
                            }
                            
                            product_type = "fabric"  # По умолчанию
                            logo_effect = material_adaptations.get(product_type, material_adaptations["fabric"]).get(
                                logo_application, material_adaptations["fabric"]["embroidery"]
                            )
                            
                            # Обработка опции "как на фото"
                            color_instruction = "keep the original color from the product image" if product_color == "как на фото" else f"make the product {product_color}"
                            angle_instruction = "keep the original angle from the product image" if product_angle == "как на фото" else f"photograph from {product_angle} angle"
                            
                            debug_prompt = f"""PART 1 - PRODUCT SETUP:
Create a product in {mockup_style} style.
Color: {color_instruction}
Photography: {angle_instruction}
Style: {style_descriptions.get(mockup_style, style_descriptions['modern'])}

PART 2 - LOGO APPLICATION:
Apply logo using {logo_application_key} method: {logo_effect}
Logo must follow product curves and texture naturally.

{f"SPECIAL REQUIREMENTS: {custom_prompt}" if custom_prompt.strip() else ""}

Final requirements:
- Professional studio lighting
- Clean background
- High quality image

Generate the mockup image."""
                            
                            st.code(debug_prompt, language="text")
                        
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
                            
                            # Показываем информацию о сохранении в историю
                            if "history_paths" in result and result["history_paths"]:
                                st.info(f"📁 Мокапы сохранены в историю: {len(result['history_paths'])} файлов")
                                for i, path in enumerate(result["history_paths"]):
                                    st.write(f"  {i+1}. {path}")
                            
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
    
    # Кнопка очистки изображений (если есть хотя бы одно изображение)
    if "product_image" in st.session_state or "logo_image" in st.session_state or "pattern_image" in st.session_state:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Очистить изображения", type="secondary", use_container_width=True):
                # Очищаем изображения из сессии
                if "product_image" in st.session_state:
                    del st.session_state.product_image
                if "logo_image" in st.session_state:
                    del st.session_state.logo_image
                if "pattern_image" in st.session_state:
                    del st.session_state.pattern_image
                st.rerun()
            
            # Кнопка очистки кэша (для разработки)
            if st.button("Обновить кэш", type="secondary", use_container_width=True, help="Очистить кэш модулей (используйте при обновлении кода)"):
                clear_batch_processor_cache()
                st.success("Кэш очищен! Перезагрузите страницу.")
    

def display_results(result: dict):
    """Отображение результатов генерации"""
    
    mockups = result.get("mockups", {})
    
    if not mockups:
        st.error("❌ Нет данных о мокапах для отображения")
        st.error(f"Доступные ключи в результате: {list(result.keys())}")
        return
    
    # Проверка, использовался ли fallback
    fallback_used = mockups.get("fallback_used", False)
    
    # Показываем только Gemini мокапы
    
    # Gemini мокапы (если есть)
    if "gemini_mockups" in mockups:
        gemini_mockups = mockups["gemini_mockups"]
        
        if gemini_mockups:
            st.subheader("🤖 AI-мокапы от Gemini 2.5 Flash")
            
            for i, mockup in enumerate(gemini_mockups):
                if "description" in mockup:
                    st.write(f"**Вариант {i+1}:** {mockup['description']}")
                
                # Если есть изображение от Gemini
                if "image_data" in mockup:
                    try:
                        from PIL import Image
                        import io
                        
                        # image_data уже является bytes от Gemini
                        image_data = mockup["image_data"]
                        image = Image.open(io.BytesIO(image_data))
                        
                        # Увеличенное превью результата для лучшего просмотра
                        st.image(image, caption=f"AI-мокап {i+1}", use_container_width=True)
                        
                        # Кнопки управления
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Кнопка скачивания
                            st.download_button(
                                label=f"📥 Скачать AI-мокап {i+1}",
                                data=image_data,
                                file_name=f"ai_mockup_{i+1}.jpg",
                                mime="image/jpeg",
                                key=f"download_ai_{i+1}",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Кнопка пересоздания
                            if st.button(f"🔄 Пересоздать {i+1}", key=f"regenerate_ai_{i+1}", use_container_width=True):
                                # Сохраняем параметры для пересоздания
                                st.session_state.regenerate_params = {
                                    "mockup_index": i,
                                    "mockup_data": mockup,
                                    "original_result": result
                                }
                                st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка отображения AI-изображения: {e}")
                        # Показываем дополнительную информацию для отладки
                        st.write(f"Тип image_data: {type(mockup['image_data'])}")
                        if hasattr(mockup['image_data'], '__len__'):
                            st.write(f"Длина image_data: {len(mockup['image_data'])}")
    
    # Информация о результате
    st.info(f"Источник: {result.get('source', 'unknown')} | "
            f"Время обработки: {result.get('processing_time', 0):.2f}с")

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
                if "batch_product_names" in st.session_state:
                    del st.session_state.batch_product_names
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
        product_name = regenerate_params["product_name"]
        
        st.info(f"🔄 Пересоздание товара: {product_name}")
        
        with st.spinner("Пересоздание товара с теми же параметрами..."):
            try:
                generator = get_mockup_generator()
                
                # Получаем параметры из оригинального промпта
                prompt_data = regenerate_params["prompt_data"]
                original_image = regenerate_params["original_image"]
                
                # Отладочная информация
                st.write(f"🔄 Пересоздание товара '{product_name}' (индекс: {item_index})")
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
                            st.success(f"✅ Товар '{product_name}' пересоздан!")
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
    
    # Загрузка логотипа и паттерна
    col1, col2 = st.columns(2)
    
    with col1:
        # Блок загрузки логотипа с правильным дизайном
        st.markdown('<div class="settings-block batch-logo-block">', unsafe_allow_html=True)
        st.markdown("### Логотип для коллекции")
        
        logo_file = st.file_uploader(
            "Загрузите логотип клиента",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="batch_logo"
        )
        
        if logo_file:
            logo_image = Image.open(logo_file)
            st.session_state.batch_logo_image = logo_image
            
            # Компактное превью логотипа
            preview_size = (80, 80)
            preview_logo = logo_image.copy()
            preview_logo.thumbnail(preview_size, Image.LANCZOS)
            st.image(preview_logo, caption="Логотип", width=80)
            st.caption(f"{logo_image.size[0]}x{logo_image.size[1]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Блок загрузки паттерна с правильным дизайном
        st.markdown('<div class="settings-block batch-pattern-block">', unsafe_allow_html=True)
        st.markdown("### Паттерн (опционально)")
        
        pattern_file = st.file_uploader(
            "Загрузите паттерн для коллекции",
            type=['jpg', 'jpeg', 'png', 'webp'],
            key="batch_pattern",
            help="Паттерн будет использован для всех товаров коллекции"
        )
        
        if pattern_file:
            pattern_image = Image.open(pattern_file)
            st.session_state.batch_pattern_image = pattern_image
            
            # Компактное превью паттерна
            preview_size = (80, 80)
            preview_pattern = pattern_image.copy()
            preview_pattern.thumbnail(preview_size, Image.LANCZOS)
            st.image(preview_pattern, caption="Паттерн", width=80)
            st.caption(f"{pattern_image.size[0]}x{pattern_image.size[1]}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Загрузка товаров с правильным дизайном
    st.markdown('<div class="settings-block batch-products-block">', unsafe_allow_html=True)
    st.markdown("### Товары для коллекции (до 10 штук)")
    
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
        st.session_state.batch_product_images = [Image.open(f) for f in product_files]
        
        # Показываем превью товаров с полями для названий
        st.markdown(f"**Загружено товаров: {len(product_files)}**")
        
        # Инициализируем названия товаров если их нет
        if "batch_product_names" not in st.session_state:
            st.session_state.batch_product_names = [f"Товар {i+1}" for i in range(len(product_files))]
        
        # Показываем товары с полями для названий
        for i, img in enumerate(st.session_state.batch_product_images):
            col1, col2 = st.columns([1, 4])
            
            with col1:
                preview_size = (80, 80)
                preview_img = img.copy()
                preview_img.thumbnail(preview_size, Image.LANCZOS)
                st.image(preview_img, width=80)
            
            with col2:
                # Поле для названия товара
                product_name = st.text_input(
                    f"Название товара {i+1}",
                    value=st.session_state.batch_product_names[i],
                    key=f"product_name_{i}",
                    help="Название товара для сохранения в результатах"
                )
                st.session_state.batch_product_names[i] = product_name
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Настройки коллекции
    if product_files and logo_file:
        st.markdown("---")
        st.markdown("**⚙️ Настройки коллекции**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Основные настройки с правильным дизайном
            st.markdown('<div class="settings-block batch-settings-block">', unsafe_allow_html=True)
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
            st.markdown('<div class="settings-block batch-additional-block">', unsafe_allow_html=True)
            st.markdown("### Дополнительно")
            
            collection_theme = st.text_input(
                "Тема коллекции",
                placeholder="Например: 'Летняя коллекция', 'Спортивная линия'",
                help="Тема или название коллекции"
            )
            
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
                            collection_style=collection_style,
                            collection_theme=collection_theme,
                            product_names=st.session_state.batch_product_names
                        )
                        
                        if analysis_result["status"] == "success":
                            st.success("✅ Анализ коллекции завершен - AI проанализировал конкретные товары и определил оптимальное нанесение логотипа")
                            st.info("🔍 AI определил тип каждого товара и выбрал реалистичное нанесение логотипа для каждого")
                            
                            # Показываем настройки коллекции
                            if custom_description.strip() or add_tag or add_person:
                                with st.expander("⚙️ Настройки коллекции"):
                                    st.write(f"**Цвет товаров:** {product_color}")
                                    st.write(f"**Стиль коллекции:** {collection_style}")
                                    if collection_theme.strip():
                                        st.write(f"**Тема коллекции:** {collection_theme}")
                                    if custom_description.strip():
                                        st.write(f"**Дополнительное описание:** {custom_description}")
                                    if add_tag:
                                        st.write("**Дополнительно:** Добавлены бирки к товарам")
                                    if add_person:
                                        st.write("**Дополнительно:** Показать товары в использовании")
                            
                            # Показываем созданные промпты
                            with st.expander("📝 Созданные промпты для товаров"):
                                for i, prompt_data in enumerate(analysis_result["individual_prompts"]):
                                    product_name = st.session_state.batch_product_names[i] if i < len(st.session_state.batch_product_names) else f"Товар {i+1}"
                                    st.write(f"**{product_name}:**")
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
                                "collection_style": collection_style,
                                "collection_theme": collection_theme
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
                            
                            for i, (product_img, prompt_data, product_name) in enumerate(zip(
                                st.session_state.batch_product_images,
                                analysis_result["individual_prompts"],
                                st.session_state.batch_product_names
                            )):
                                # Обновляем прогресс
                                progress = (i + 1) / total_items
                                progress_bar.progress(progress)
                                status_text.text(f"Обработка {i+1}/{total_items}: {product_name}")
                                
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
                                            "product_name": product_name,
                                            "original_image": product_img,
                                            "mockup": mockup_result[0],
                                            "prompt_data": prompt_data,
                                            "status": "success"
                                        })
                                    else:
                                        results.append({
                                            "index": i,
                                            "product_name": product_name,
                                            "original_image": product_img,
                                            "mockup": None,
                                            "prompt_data": prompt_data,
                                            "status": "error",
                                            "error": "Не удалось сгенерировать мокап"
                                        })
                                except Exception as e:
                                    results.append({
                                        "index": i,
                                        "product_name": product_name,
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
                                "collection_style": collection_style,
                                "collection_theme": collection_theme
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
                            
                            for i, (product_img, prompt_data, product_name) in enumerate(zip(
                                st.session_state.batch_product_images,
                                analysis_result["individual_prompts"],
                                st.session_state.batch_product_names
                            )):
                                # Обновляем прогресс
                                progress = (i + 1) / total_items
                                progress_bar.progress(progress)
                                status_text.text(f"Обработка {i+1}/{total_items}: {product_name}")
                                
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
                                            "product_name": product_name,
                                            "original_image": product_img,
                                            "mockup": mockup_result[0],
                                            "prompt_data": prompt_data,
                                            "status": "success"
                                        })
                                    else:
                                        results.append({
                                            "index": i,
                                            "product_name": product_name,
                                            "original_image": product_img,
                                            "mockup": None,
                                            "prompt_data": prompt_data,
                                            "status": "error",
                                            "error": "Не удалось сгенерировать мокап"
                                        })
                                except Exception as e:
                                    results.append({
                                        "index": i,
                                        "product_name": product_name,
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
                                
                                image_data = result["mockup"]["image_data"]
                                image = Image.open(io.BytesIO(image_data))
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
                                
                                with col_regenerate:
                                    # Кнопка пересоздания
                                    if st.button(f"🔄 Пересоздать", key=f"regenerate_batch_{result['index']}", use_container_width=True):
                                        # Сохраняем параметры для пересоздания
                                        st.session_state.batch_regenerate_params = {
                                            "item_index": result['index'],
                                            "product_name": product_name,
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

if __name__ == "__main__":
    main()
