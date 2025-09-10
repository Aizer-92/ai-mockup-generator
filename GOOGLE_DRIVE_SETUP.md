# 📁 Настройка Google Drive API

## Обзор

Интеграция с Google Drive позволяет:
- ✅ **Хранить мокапы** в облаке Google Drive
- ✅ **Отображать галерею** прямо из Google Drive
- ✅ **Синхронизировать** между устройствами
- ✅ **Неограниченное хранилище** (в рамках лимитов Google)

## Настройка Google Cloud Console

### 1. Создание проекта

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Drive API:
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Google Drive API"
   - Нажмите "Enable"

### 2. Создание учетных данных

1. Перейдите в "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth client ID"
3. Выберите "Desktop application"
4. Дайте название (например: "AI Mockup Generator")
5. Скачайте JSON файл с учетными данными

### 3. Настройка OAuth consent screen

1. Перейдите в "APIs & Services" → "OAuth consent screen"
2. Выберите "External" (для личного использования)
3. Заполните обязательные поля:
   - App name: "AI Mockup Generator"
   - User support email: ваш email
   - Developer contact: ваш email
4. Добавьте scopes:
   - `https://www.googleapis.com/auth/drive.file`
5. Добавьте тестовых пользователей (ваш email)

## Настройка приложения

### 1. Файл credentials.json

Поместите скачанный JSON файл в корень проекта как `credentials.json`:

```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 2. Переменные окружения

Добавьте в `.env` или `.streamlit/secrets.toml`:

```env
# Google Drive настройки
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_NAME=AI Mockup Generator

# Остальные настройки
GEMINI_API_KEY=your_gemini_api_key
AUTH_ENABLED=true
AUTH_PASSWORD=your_password
```

### 3. Первый запуск

При первом запуске:
1. Откроется браузер для авторизации
2. Войдите в свой Google аккаунт
3. Разрешите доступ к Google Drive
4. Создастся файл `token.json` с токеном доступа

## Использование

### Автоматическая загрузка

После настройки все сгенерированные мокапы будут автоматически загружаться в Google Drive в папку "AI Mockup Generator".

### Галерея из Google Drive

Галерея будет автоматически загружать мокапы из Google Drive и отображать их с метаданными.

### Управление файлами

- **Просмотр**: Все мокапы доступны в галерее
- **Скачивание**: Кнопка скачивания для каждого мокапа
- **Удаление**: Возможность удаления старых мокапов

## Безопасность

### Права доступа

- Приложение имеет доступ только к файлам, которые оно создает
- Не может видеть другие файлы в Google Drive
- Токен доступа хранится локально в `token.json`

### Рекомендации

- ✅ Не делитесь файлом `credentials.json`
- ✅ Добавьте `token.json` в `.gitignore`
- ✅ Регулярно обновляйте токены доступа
- ✅ Используйте отдельный Google аккаунт для приложения

## Устранение неполадок

### Ошибка "credentials.json not found"

- Убедитесь, что файл `credentials.json` находится в корне проекта
- Проверьте правильность скачанного файла

### Ошибка "Access denied"

- Проверьте настройки OAuth consent screen
- Убедитесь, что ваш email добавлен в тестовые пользователи
- Проверьте включен ли Google Drive API

### Ошибка "Token expired"

- Удалите файл `token.json`
- Перезапустите приложение для повторной авторизации

### Ошибка "Quota exceeded"

- Проверьте лимиты Google Drive API
- Удалите старые мокапы для освобождения места

## Лимиты Google Drive API

- **100 запросов в 100 секунд** на пользователя
- **1000 запросов в 100 секунд** на проект
- **15 ГБ бесплатного хранилища** в Google Drive
- **Максимум 5 МБ** на файл для бесплатного аккаунта

## Альтернативы

Если Google Drive не подходит, можно использовать:
- **Dropbox API** - аналогичная интеграция
- **AWS S3** - облачное хранилище
- **Firebase Storage** - от Google
- **OneDrive API** - от Microsoft
