# 🔐 Быстрый старт - Безопасность

## Включение аутентификации

### 1. Настройка .env файла
```bash
# Скопируйте пример
cp env_example.txt .env

# Отредактируйте .env
AUTH_ENABLED=true
AUTH_PASSWORD=your_secure_password_here
```

### 2. Перезапуск приложения
```bash
# Остановите приложение (Ctrl+C)
# Запустите заново
streamlit run main.py
```

### 3. Вход в систему
- Откройте http://localhost:8501
- Введите пароль из .env файла
- Нажмите "🚀 Войти"

## Отключение аутентификации (для разработки)

```bash
# В .env файле
AUTH_ENABLED=false
```

## Деплой с аутентификацией

### Streamlit Cloud
```bash
# В настройках секретов
AUTH_ENABLED = "true"
AUTH_PASSWORD = "your_secure_password"
```

### Railway
```bash
# В переменных окружения
AUTH_ENABLED=true
AUTH_PASSWORD=your_secure_password
```

## Безопасность

⚠️ **Важно**: 
- Используйте сложные пароли в продакшне
- Никогда не коммитьте .env файлы
- Регулярно меняйте пароли

## Пароль по умолчанию
`admin123` - **СМЕНИТЕ ПРИ ДЕПЛОЕ!**
