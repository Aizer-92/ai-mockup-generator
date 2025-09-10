"""
Модуль аутентификации для AI Mockup Generator
Простая система аутентификации с паролем
"""
import streamlit as st
import hashlib
import time
from config import get_config

# Получаем конфигурацию аутентификации
config = get_config()
AUTH_ENABLED = config['AUTH_ENABLED']
AUTH_PASSWORD = config['AUTH_PASSWORD']
AUTH_SESSION_KEY = 'authenticated'

def hash_password(password: str) -> str:
    """Хеширование пароля для безопасности"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str) -> bool:
    """Проверка пароля"""
    if not AUTH_ENABLED:
        return True
    
    hashed_input = hash_password(password)
    hashed_stored = hash_password(AUTH_PASSWORD)
    return hashed_input == hashed_stored

def is_authenticated() -> bool:
    """Проверка, аутентифицирован ли пользователь"""
    try:
        if not AUTH_ENABLED:
            return True
        
        # Простая проверка сессии
        return st.session_state.get(AUTH_SESSION_KEY, False)
    except Exception as e:
        # Отладочная информация для диагностики
        print(f"ERROR in is_authenticated: {e}")
        print(f"AUTH_ENABLED: {AUTH_ENABLED}")
        print(f"AUTH_SESSION_KEY: {AUTH_SESSION_KEY}")
        # Возвращаем False в случае ошибки
        return False

def login_form() -> bool:
    """Отображение формы входа"""
    if not AUTH_ENABLED:
        return True
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 AI Mockup Generator</h1>
        <p style="color: #666; font-size: 1.1rem;">Введите пароль для доступа к приложению</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Центрируем форму входа
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        with st.form("login_form"):
            st.markdown("### 🔑 Вход в систему")
            
            password = st.text_input(
                "Пароль",
                type="password",
                placeholder="Введите пароль",
                help="Введите пароль для доступа к приложению"
            )
            
            submitted = st.form_submit_button("🚀 Войти", type="primary", use_container_width=True)
            
            if submitted:
                if check_password(password):
                    st.session_state[AUTH_SESSION_KEY] = True
                    st.session_state['last_activity'] = time.time()
                    st.success("✅ Успешный вход!")
                    st.rerun()
                else:
                    st.error("❌ Неверный пароль!")
        
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
            - 🔐 Доступ защищен паролем
            - 🛡️ Все данные обрабатываются локально
            - 🔒 API ключи хранятся в переменных окружения
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
            st.session_state[AUTH_SESSION_KEY] = False
            st.rerun()

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
        return "🔐 Аутентифицирован"
    else:
        return "🔒 Не аутентифицирован"

def get_user_info():
    """Получение информации о пользователе (для совместимости)"""
    if not AUTH_ENABLED or not is_authenticated():
        return None
    
    return {
        'name': 'Пользователь',
        'email': 'user@example.com',
        'is_logged_in': True
    }