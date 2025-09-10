# 🚀 Настройка Google Drive для Streamlit приложения

## Обзор

Эта инструкция поможет настроить Google Drive API для вашего Streamlit приложения AI Mockup Generator. После настройки все сгенерированные мокапы будут автоматически сохраняться в Google Drive.

## 🎯 Быстрая настройка (5 минут)

### 1. Google Cloud Console

#### Шаг 1: Перейдите в Google Cloud Console
1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите проект: **quickstart-1591698112539**
3. Если проекта нет, создайте новый

#### Шаг 2: Включите Google Drive API
1. Перейдите в **APIs & Services** → **Library**
2. Найдите "Google Drive API"
3. Нажмите **Enable**
4. Подождите активации (1-2 минуты)

#### Шаг 3: Настройте OAuth Consent Screen
1. Перейдите в **APIs & Services** → **OAuth consent screen**
2. Выберите **External** (для личного использования)
3. Заполните обязательные поля:
   - **App name**: `AI Mockup Generator`
   - **User support email**: ваш email
   - **Developer contact**: ваш email
4. В разделе **Scopes** добавьте:
   - `https://www.googleapis.com/auth/drive.file`
5. В разделе **Test users** добавьте:
   - ваш email
6. Нажмите **Save**

#### Шаг 4: Создайте OAuth 2.0 Credentials
1. Перейдите в **APIs & Services** → **Credentials**
2. Нажмите **+ CREATE CREDENTIALS** → **OAuth client ID**
3. Выберите **Desktop application**
4. Название: `AI Mockup Generator Desktop`
5. Нажмите **Create**
6. Скачайте JSON файл и переименуйте в `credentials.json`
7. Поместите файл в корень проекта

#### Шаг 5: Настройте Redirect URIs
1. Найдите созданный OAuth 2.0 Client ID
2. Нажмите на иконку редактирования (карандаш)
3. В разделе **Authorized redirect URIs** добавьте:
   ```
   http://localhost:8080
   http://localhost:8081
   http://localhost:8082
   http://localhost:8083
   http://localhost:8084
   http://localhost:8085
   http://localhost:8086
   http://localhost:8087
   http://localhost:8088
   http://localhost:8089
   http://localhost:8090
   ```
4. Нажмите **Save**

### 2. Настройка Streamlit приложения

#### Шаг 1: Установите зависимости
```bash
pip install -r requirements.txt
```

#### Шаг 2: Настройте переменные окружения
Создайте файл `.env` в корне проекта:
```env
# Основные настройки
GEMINI_API_KEY=your_gemini_api_key_here
AUTH_ENABLED=true
AUTH_PASSWORD=your_password_here

# Google Drive (включить после настройки)
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_NAME=AI Mockup Generator
```

#### Шаг 3: Запустите приложение
```bash
streamlit run main.py
```

### 3. Первая авторизация

При первом запуске:
1. Откроется браузер для авторизации Google
2. Войдите в свой Google аккаунт
3. Разрешите доступ к Google Drive
4. Создастся файл `token.json` с токеном доступа

## 🔧 Детальная настройка

### Структура файлов
```
mockup_generator/
├── main.py                    # Streamlit приложение
├── google_drive_client.py     # Google Drive API клиент
├── credentials.json           # OAuth credentials (скачать из Google Cloud)
├── token.json                 # Токен доступа (создается автоматически)
├── .env                       # Переменные окружения
└── requirements.txt           # Python зависимости
```

### Переменные окружения

#### Обязательные:
```env
GEMINI_API_KEY=your_gemini_api_key_here
AUTH_ENABLED=true
AUTH_PASSWORD=your_password_here
```

#### Google Drive (опционально):
```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_FOLDER_NAME=AI Mockup Generator
```

### Настройка для Streamlit Cloud

Для деплоя на Streamlit Cloud:

1. **Добавьте в Streamlit Secrets:**
   ```toml
   # .streamlit/secrets.toml
   GEMINI_API_KEY = "your_gemini_api_key"
   AUTH_ENABLED = true
   AUTH_PASSWORD = "your_password"
   GOOGLE_DRIVE_ENABLED = true
   GOOGLE_DRIVE_FOLDER_NAME = "AI Mockup Generator"
   ```

2. **Загрузите credentials.json:**
   - В настройках Streamlit Cloud
   - Добавьте файл `credentials.json`
   - Убедитесь, что файл доступен в приложении

3. **Настройте redirect URIs для production:**
   - Добавьте URL вашего Streamlit приложения
   - Например: `https://your-app-name.streamlit.app`

## 🧪 Тестирование

### Локальное тестирование
```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите приложение
streamlit run main.py

# Откройте http://localhost:8501
```

### Проверка Google Drive
1. Сгенерируйте тестовый мокап
2. Проверьте папку "AI Mockup Generator" в Google Drive
3. Убедитесь, что файл загрузился с метаданными

## 🚨 Устранение неполадок

### Ошибка "redirect_uri_mismatch"
**Проблема**: Неправильные redirect URIs в Google Cloud Console
**Решение**: 
1. Перейдите в Google Cloud Console → Credentials
2. Найдите ваш OAuth 2.0 Client ID
3. Добавьте redirect URIs (см. Шаг 5 выше)
4. Сохраните изменения

### Ошибка "access_denied"
**Проблема**: Не настроен OAuth consent screen
**Решение**:
1. Перейдите в OAuth consent screen
2. Добавьте ваш email в Test users
3. Убедитесь, что добавлен scope `https://www.googleapis.com/auth/drive.file`

### Ошибка "API not enabled"
**Проблема**: Google Drive API не включен
**Решение**:
1. Перейдите в APIs & Services → Library
2. Найдите "Google Drive API"
3. Нажмите "Enable"

### Файл credentials.json не найден
**Проблема**: Не скачан файл credentials из Google Cloud Console
**Решение**:
1. Перейдите в Credentials
2. Скачайте JSON файл для Desktop application
3. Переименуйте в `credentials.json`
4. Поместите в корень проекта

## 📋 Чек-лист настройки

- [ ] Создан проект в Google Cloud Console
- [ ] Включен Google Drive API
- [ ] Настроен OAuth consent screen
- [ ] Создан OAuth 2.0 Client ID (Desktop application)
- [ ] Добавлены redirect URIs
- [ ] Скачан и размещен credentials.json
- [ ] Настроены переменные окружения
- [ ] Запущено приложение Streamlit
- [ ] Выполнена первая авторизация
- [ ] Протестирована загрузка в Google Drive

## 🎉 Готово!

После выполнения всех шагов:
- ✅ Все мокапы автоматически загружаются в Google Drive
- ✅ Галерея отображает мокапы из облака
- ✅ Синхронизация между устройствами
- ✅ Неограниченное хранилище (в рамках лимитов Google)

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте чек-лист выше
2. Убедитесь, что все настройки сохранены в Google Cloud Console
3. Подождите 2-3 минуты для применения изменений
4. Очистите кэш браузера
5. Попробуйте в режиме инкогнито

## 🔗 Полезные ссылки

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OAuth 2.0 Scopes](https://developers.google.com/identity/protocols/oauth2/scopes)
