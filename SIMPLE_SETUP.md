# 🚀 Простая настройка AI Mockup Generator

## Быстрый старт

### 1. Переменные окружения

Создайте файл `.env` в корне проекта:

```env
GEMINI_API_KEY=your_gemini_api_key_here
AUTH_ENABLED=true
AUTH_PASSWORD=your_password_here
```

### 2. Или используйте Streamlit secrets

Создайте файл `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
AUTH_ENABLED = true
AUTH_PASSWORD = "your_password_here"
```

### 3. Запуск

```bash
pip install -r requirements.txt
streamlit run main.py
```

## Настройки

- **AUTH_ENABLED** - включить/выключить аутентификацию (true/false)
- **AUTH_PASSWORD** - пароль для входа в приложение
- **GEMINI_API_KEY** - API ключ от Google Gemini

## Отключение аутентификации

Для отключения аутентификации установите:
```env
AUTH_ENABLED=false
```

## Получение Gemini API Key

1. Перейдите на https://makersuite.google.com/app/apikey
2. Создайте новый API ключ
3. Скопируйте ключ в переменную GEMINI_API_KEY
