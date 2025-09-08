# 🚀 Деплой AI Mockup Generator

## Обзор

AI Mockup Generator готов к деплою на различных платформах. Выберите подходящий вариант для ваших нужд.

## 🌐 Платформы для деплоя

### 1. Streamlit Cloud (Рекомендуется)

**Преимущества:**
- Бесплатно
- Простая настройка
- Автоматический деплой из GitHub
- Встроенная поддержка Streamlit

**Шаги:**
1. Загрузите код в GitHub репозиторий
2. Перейдите на [share.streamlit.io](https://share.streamlit.io)
3. Подключите GitHub репозиторий
4. Настройте секреты:
   ```
   GEMINI_API_KEY = "your_gemini_api_key"
   AUTH_ENABLED = "true"
   AUTH_PASSWORD = "your_secure_password"
   ```
5. Нажмите "Deploy"

### 2. Railway

**Преимущества:**
- Быстрый деплой
- Автоматическое масштабирование
- Простая настройка переменных окружения

**Шаги:**
1. Загрузите код в GitHub репозиторий
2. Перейдите на [railway.app](https://railway.app)
3. Подключите GitHub репозиторий
4. Настройте переменные окружения:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   AUTH_ENABLED=true
   AUTH_PASSWORD=your_secure_password
   ```
5. Railway автоматически задеплоит приложение

### 3. Heroku

**Преимущества:**
- Надежная платформа
- Множество аддонов
- Хорошая документация

**Шаги:**
1. Установите Heroku CLI
2. Создайте приложение:
   ```bash
   heroku create your-app-name
   ```
3. Настройте переменные окружения:
   ```bash
   heroku config:set GEMINI_API_KEY=your_gemini_api_key
   heroku config:set AUTH_ENABLED=true
   heroku config:set AUTH_PASSWORD=your_secure_password
   ```
4. Задеплойте:
   ```bash
   git push heroku main
   ```

### 4. Google Cloud Run

**Преимущества:**
- Платите только за использование
- Автоматическое масштабирование
- Интеграция с Google Cloud

**Шаги:**
1. Установите Google Cloud CLI
2. Создайте проект в Google Cloud Console
3. Включите Cloud Run API
4. Соберите и задеплойте:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/mockup-generator
   gcloud run deploy --image gcr.io/PROJECT-ID/mockup-generator --platform managed
   ```

### 5. Docker

**Для локального запуска:**
```bash
# Сборка образа
docker build -t mockup-generator .

# Запуск контейнера
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_gemini_api_key \
  -e AUTH_ENABLED=true \
  -e AUTH_PASSWORD=your_secure_password \
  mockup-generator
```

**С docker-compose:**
```bash
# Создайте .env файл с переменными
echo "GEMINI_API_KEY=your_gemini_api_key" > .env

# Запустите
docker-compose up -d
```

## 🔐 Настройка безопасности

### Обязательные переменные окружения

```env
# API ключ Gemini (обязательно)
GEMINI_API_KEY=your_gemini_api_key_here

# Аутентификация (рекомендуется для продакшна)
AUTH_ENABLED=true
AUTH_PASSWORD=your_secure_password_here
```

### Рекомендации по безопасности

1. **Используйте сложные пароли** (минимум 12 символов)
2. **Регулярно меняйте пароли**
3. **Не коммитьте .env файлы** в репозиторий
4. **Используйте HTTPS** для продакшна
5. **Настройте мониторинг** и логирование

## 📊 Мониторинг и логи

### Streamlit Cloud
- Логи доступны в панели управления
- Автоматический мониторинг здоровья

### Railway
- Встроенные метрики и логи
- Уведомления об ошибках

### Heroku
- Heroku Logs для просмотра логов
- New Relic для мониторинга производительности

## 🔧 Устранение неполадок

### Частые проблемы

**Ошибка: "GEMINI_API_KEY не найден"**
- Проверьте переменные окружения
- Убедитесь, что API ключ действителен

**Ошибка: "Неверный пароль"**
- Проверьте переменную AUTH_PASSWORD
- Убедитесь, что AUTH_ENABLED=true

**Приложение не запускается**
- Проверьте логи деплоя
- Убедитесь, что все зависимости установлены

### Получение логов

**Streamlit Cloud:**
- Логи в панели управления приложения

**Railway:**
```bash
railway logs
```

**Heroku:**
```bash
heroku logs --tail
```

## 🎯 Готово к деплою!

Выберите подходящую платформу и следуйте инструкциям. Все необходимые файлы конфигурации уже созданы:

- ✅ `requirements.txt` - зависимости Python
- ✅ `Dockerfile` - для контейнеризации
- ✅ `docker-compose.yml` - для локальной разработки
- ✅ `Procfile` - для Heroku
- ✅ `railway.json` - для Railway
- ✅ `.streamlit/config.toml` - для Streamlit Cloud

**Удачного деплоя! 🚀**
