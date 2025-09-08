# 🔧 Установка переменных окружения

## Быстрая установка

### 1. Установка переменных в терминале
```bash
# Включить аутентификацию
export AUTH_ENABLED=true

# Установить пароль
export AUTH_PASSWORD=admin123

# Проверить установку
echo "AUTH_ENABLED: $AUTH_ENABLED"
echo "AUTH_PASSWORD: $AUTH_PASSWORD"
```

### 2. Настройка .env файла
```bash
# Создать .env файл
cp env_example.txt .env

# Отредактировать .env
AUTH_ENABLED=true
AUTH_PASSWORD=admin123
```

### 3. Проверка работы
```bash
# Запустить приложение
streamlit run main.py

# Открыть в браузере
# http://localhost:8501
# Пароль: admin123
```

## Для разработки (отключить аутентификацию)

```bash
export AUTH_ENABLED=false
```

## Для продакшна (изменить пароль)

```bash
export AUTH_PASSWORD=your_secure_password_here
```

## Проверка переменных

```bash
# Показать все переменные
env | grep AUTH

# Проверить конкретную переменную
echo $AUTH_ENABLED
echo $AUTH_PASSWORD
```

## Готово! ✅

Переменные окружения установлены и приложение готово к работе с аутентификацией.
