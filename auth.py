"""
Модуль аутентификации для AI Mockup Generator
Использует официальную систему аутентификации Streamlit с OIDC
"""
import streamlit as st
from config import get_config

# Получаем конфигурацию аутентификации
config = get_config()
AUTH_ENABLED = config['AUTH_ENABLED']

def is_authenticated() -> bool:
    """Проверка, аутентифицирован ли пользователь"""
    if not AUTH_ENABLED:
        return True
    
    # Используем официальную систему аутентификации Streamlit
    return st.user.is_logged_in

def login_form() -> bool:
    """Отображение формы входа"""
    if not AUTH_ENABLED:
        return True
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 AI Mockup Generator</h1>
        <p style="color: #666; font-size: 1.1rem;">Войдите в систему для доступа к приложению</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Центрируем форму входа
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        st.markdown("### 🔑 Вход в систему")
        
        # Проверяем, настроена ли аутентификация
        try:
            # Пытаемся использовать официальную аутентификацию Streamlit
            if st.button("🚀 Войти через Google", type="primary", use_container_width=True):
                st.login("google")
            
            st.markdown("---")
            
            # Информация о системе
            with st.expander("ℹ️ Информация о системе"):
                st.markdown("""
                **AI Mockup Generator** - это инструмент для создания профессиональных мокапов товаров с логотипами клиентов.
                
                **Возможности:**
                - 🎨 AI-генерация мокапов с Gemini 2.5 Flash
                - 🏷️ Реалистичная интеграция логотипов
                - 📦 Пакетная обработка коллекций
                - 🎯 Настройка стилей и параметров
                - 💾 Кэширование результатов
                
                **Безопасность:**
                - 🔐 Безопасная аутентификация через Google
                - 🛡️ Защищенное хранение данных
                - 🔒 Автоматическое управление сессиями
                """)
                
                st.info("💡 Для настройки аутентификации обратитесь к администратору системы")
        
        except Exception as e:
            st.error("❌ Ошибка настройки аутентификации")
            st.error(f"Детали: {str(e)}")
            
            with st.expander("🔧 Информация для разработчика"):
                st.markdown("""
                **Ошибка настройки аутентификации**
                
                Убедитесь, что в `.streamlit/secrets.toml` настроена конфигурация OIDC:
                
                ```toml
                [auth]
                redirect_uri = "http://localhost:8501/oauth2callback"
                cookie_secret = "your-secret-key"
                
                [auth.google]
                client_id = "your-google-client-id"
                client_secret = "your-google-client-secret"
                server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
                ```
                """)
    
    return False

def logout_button():
    """Кнопка выхода"""
    if not AUTH_ENABLED:
        return
    
    # Размещаем кнопку выхода в правом верхнем углу
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col3:
        if st.button("🚪 Выйти", type="secondary", help="Выйти из системы"):
            st.logout()

def require_auth(func):
    """Декоратор для защиты функций аутентификацией"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            login_form()
            return None
        return func(*args, **kwargs)
    return wrapper

def auth_status():
    """Показывает статус аутентификации"""
    if not AUTH_ENABLED:
        return "🔓 Аутентификация отключена"
    
    if is_authenticated():
        user_name = st.user.name if hasattr(st.user, 'name') and st.user.name else "Пользователь"
        return f"🔐 Аутентифицирован как {user_name}"
    else:
        return "🔒 Не аутентифицирован"

def get_user_info():
    """Получение информации о пользователе"""
    if not AUTH_ENABLED or not is_authenticated():
        return None
    
    return {
        'name': getattr(st.user, 'name', 'Неизвестно'),
        'email': getattr(st.user, 'email', 'Неизвестно'),
        'is_logged_in': st.user.is_logged_in
    }