# 🔐 Настройка аутентификации для AI Mockup Generator

## Обзор

AI Mockup Generator теперь включает систему аутентификации для защиты от публичного доступа при деплое.

## 🚀 Быстрая настройка

### 1. Локальная разработка (аутентификация отключена)
```bash
# В файле .env или переменных окружения
AUTH_ENABLED=false
```

### 2. Продакшн деплой (аутентификация включена)
```bash
# В файле .env или переменных окружения
AUTH_ENABLED=true
AUTH_PASSWORD=your_secure_password_here
```

## ⚙️ Настройка переменных окружения

### Создание файла .env
Скопируйте `env_example.txt` в `.env` и настройте:

```bash
cp env_example.txt .env
```

### Переменные окружения

| Переменная | Описание | По умолчанию | Обязательная |
|------------|----------|--------------|--------------|
| `AUTH_ENABLED` | Включить/выключить аутентификацию | `true` | Нет |
| `AUTH_PASSWORD` | Пароль для входа | `admin123` | Да (при AUTH_ENABLED=true) |
| `GEMINI_API_KEY` | API ключ Gemini | - | Да |

### Пример .env файла
```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Аутентификация
AUTH_ENABLED=true
AUTH_PASSWORD=my_secure_password_123

# Приложение
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
```

## 🔒 Безопасность

### Рекомендации по паролю
- Используйте сложный пароль (минимум 8 символов)
- Включайте буквы, цифры и специальные символы
- Не используйте пароли по умолчанию в продакшне

### Примеры безопасных паролей
```
MyApp2024!Secure
MockupGen#2024
AI_Generator$123
```

## 🌐 Деплой на различных платформах

### Streamlit Cloud
```bash
# В настройках секретов Streamlit Cloud
AUTH_ENABLED = "true"
AUTH_PASSWORD = "your_secure_password"
GEMINI_API_KEY = "your_gemini_api_key"
```

### Railway
```bash
# В настройках переменных окружения Railway
AUTH_ENABLED=true
AUTH_PASSWORD=your_secure_password
GEMINI_API_KEY=your_gemini_api_key
```

### Heroku
```bash
# Через Heroku CLI
heroku config:set AUTH_ENABLED=true
heroku config:set AUTH_PASSWORD=your_secure_password
heroku config:set GEMINI_API_KEY=your_gemini_api_key
```

### Docker
```dockerfile
# В Dockerfile или docker-compose.yml
ENV AUTH_ENABLED=true
ENV AUTH_PASSWORD=your_secure_password
ENV GEMINI_API_KEY=your_gemini_api_key
```

## 🎯 Использование

### Вход в систему
1. Откройте приложение
2. Введите пароль в поле "Пароль"
3. Нажмите "🚀 Войти"

### Выход из системы
- Нажмите кнопку "🚪 Выйти" в правом верхнем углу

### Отключение аутентификации
```bash
# Для локальной разработки
AUTH_ENABLED=false
```

## 🔧 Устранение неполадок

### Проблема: Не могу войти в систему
**Решение:**
1. Проверьте переменную `AUTH_PASSWORD` в .env файле
2. Убедитесь, что `AUTH_ENABLED=true`
3. Перезапустите приложение

### Проблема: Аутентификация не работает после деплоя
**Решение:**
1. Проверьте переменные окружения на платформе деплоя
2. Убедитесь, что переменные установлены правильно
3. Проверьте логи приложения

### Проблема: Забыл пароль
**Решение:**
1. Измените переменную `AUTH_PASSWORD` в .env файле
2. Перезапустите приложение
3. Войдите с новым паролем

## 📝 Логи и отладка

### Проверка статуса аутентификации
В коде приложения можно проверить статус:
```python
from auth import auth_status
print(auth_status())  # 🔐 Аутентифицирован / 🔒 Не аутентифицирован
```

### Отладочная информация
```python
from auth import AUTH_ENABLED, AUTH_PASSWORD
print(f"Auth enabled: {AUTH_ENABLED}")
print(f"Password set: {bool(AUTH_PASSWORD)}")
```

## 🚀 Готово к деплою!

После настройки аутентификации ваше приложение готово к безопасному деплою:

1. ✅ Защищено паролем
2. ✅ Настроено через переменные окружения
3. ✅ Совместимо с популярными платформами деплоя
4. ✅ Легко отключается для разработки

**Важно:** Всегда используйте сложные пароли в продакшне и никогда не коммитьте .env файлы в репозиторий!
