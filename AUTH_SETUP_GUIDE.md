# 🔐 Руководство по настройке аутентификации

## Обзор

Приложение теперь использует официальную систему аутентификации Streamlit с поддержкой OIDC (OpenID Connect). Это обеспечивает:

- ✅ Безопасную аутентификацию через Google/Microsoft
- ✅ Автоматическое управление сессиями
- ✅ Защищенные cookies
- ✅ Персистентность сессий между перезагрузками

## Настройка Google OAuth

### 1. Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API

### 2. Настройка OAuth 2.0

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth 2.0 Client IDs"
3. Выберите "Web application"
4. Добавьте авторизованные URI перенаправления:
   - Для разработки: `http://localhost:8501/oauth2callback`
   - Для продакшена: `https://your-app.streamlit.app/oauth2callback`

### 3. Получение учетных данных

После создания OAuth клиента вы получите:
- `client_id` (например: `123456789.apps.googleusercontent.com`)
- `client_secret` (например: `GOCSPX-abcdef123456`)

## Настройка secrets.toml

### 1. Создание файла конфигурации

Создайте файл `.streamlit/secrets.toml` в корне проекта:

```toml
# Настройки аутентификации
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-super-secret-cookie-key-change-this"

# Конфигурация Google OAuth
[auth.google]
client_id = "your-google-client-id.apps.googleusercontent.com"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

# Настройки приложения
GEMINI_API_KEY = "your-gemini-api-key"
AUTH_ENABLED = true
```

### 2. Генерация cookie_secret

Сгенерируйте случайный секретный ключ:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Альтернативные провайдеры

### Microsoft Azure AD

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-secret-key"

[auth.microsoft]
client_id = "your-microsoft-client-id"
client_secret = "your-microsoft-client-secret"
server_metadata_url = "https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"
```

### Okta

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-secret-key"

[auth.okta]
client_id = "your-okta-client-id"
client_secret = "your-okta-client-secret"
server_metadata_url = "https://{subdomain}.okta.com/.well-known/openid-configuration"
```

## Развертывание

### Streamlit Cloud

1. Загрузите код в GitHub
2. В Streamlit Cloud добавьте секреты:
   - `auth.redirect_uri`: `https://your-app.streamlit.app/oauth2callback`
   - `auth.cookie_secret`: ваш секретный ключ
   - `auth.google.client_id`: ваш Google client ID
   - `auth.google.client_secret`: ваш Google client secret
   - `auth.google.server_metadata_url`: `https://accounts.google.com/.well-known/openid-configuration`

### Локальная разработка

1. Установите зависимости:
   ```bash
   pip install streamlit[auth]
   ```

2. Создайте `.streamlit/secrets.toml` с вашими настройками

3. Запустите приложение:
   ```bash
   streamlit run main.py
   ```

## Безопасность

### Рекомендации

- ✅ Используйте HTTPS в продакшене
- ✅ Регулярно обновляйте cookie_secret
- ✅ Ограничьте доступ к OAuth клиентам
- ✅ Мониторьте использование API

### Ограничения

- ❌ Аутентификация не поддерживается для встроенных приложений
- ❌ Cookies истекают через 30 дней без активности
- ❌ Нельзя использовать generic OAuth провайдеров (только OIDC)

## Устранение неполадок

### Ошибка "Invalid redirect_uri"

- Проверьте, что redirect_uri в secrets.toml совпадает с настройками в Google Console
- Убедитесь, что используется правильный протокол (http/https)

### Ошибка "Invalid client"

- Проверьте правильность client_id и client_secret
- Убедитесь, что OAuth клиент активен в Google Console

### Сессия не сохраняется

- Проверьте настройки cookie_secret
- Убедитесь, что браузер поддерживает cookies
- Проверьте настройки CORS

## Миграция с парольной аутентификации

Если у вас была настроена парольная аутентификация:

1. Установите `streamlit[auth]`
2. Настройте OIDC провайдера
3. Обновите `AUTH_ENABLED = true` в secrets.toml
4. Перезапустите приложение

Старые настройки паролей будут проигнорированы.
