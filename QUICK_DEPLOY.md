# 🚀 Быстрый деплой AI Mockup Generator

## ✅ Репозиторий создан!

**GitHub:** https://github.com/Aizer-92/ai-mockup-generator

## 🔐 Безопасность проверена

- ✅ API ключи НЕ попали в репозиторий
- ✅ .env файлы исключены из Git
- ✅ Только примеры и документация содержат упоминания API ключей

## 🌐 Варианты деплоя

### 1. Streamlit Cloud (Рекомендуется)

1. Перейдите на [share.streamlit.io](https://share.streamlit.io)
2. Нажмите "New app"
3. Выберите репозиторий: `Aizer-92/ai-mockup-generator`
4. Настройте секреты:
   ```
   GEMINI_API_KEY = "your_gemini_api_key"
   AUTH_ENABLED = "true"
   AUTH_PASSWORD = "your_secure_password"
   ```
5. Нажмите "Deploy"

### 2. Railway

1. Перейдите на [railway.app](https://railway.app)
2. Нажмите "Deploy from GitHub repo"
3. Выберите `Aizer-92/ai-mockup-generator`
4. Настройте переменные окружения:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   AUTH_ENABLED=true
   AUTH_PASSWORD=your_secure_password
   ```

### 3. Heroku

```bash
# Клонируйте репозиторий
git clone https://github.com/Aizer-92/ai-mockup-generator.git
cd ai-mockup-generator

# Создайте приложение
heroku create your-app-name

# Настройте переменные
heroku config:set GEMINI_API_KEY=your_gemini_api_key
heroku config:set AUTH_ENABLED=true
heroku config:set AUTH_PASSWORD=your_secure_password

# Задеплойте
git push heroku main
```

## 🔧 Локальный запуск

```bash
# Клонируйте репозиторий
git clone https://github.com/Aizer-92/ai-mockup-generator.git
cd ai-mockup-generator

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
cp env_example.txt .env
# Отредактируйте .env файл

# Запустите приложение
streamlit run main.py
```

## 🐳 Docker

```bash
# Клонируйте репозиторий
git clone https://github.com/Aizer-92/ai-mockup-generator.git
cd ai-mockup-generator

# Создайте .env файл
echo "GEMINI_API_KEY=your_gemini_api_key" > .env
echo "AUTH_ENABLED=true" >> .env
echo "AUTH_PASSWORD=your_secure_password" >> .env

# Запустите с Docker Compose
docker-compose up -d
```

## 📋 Что включено

- ✅ Полная система генерации мокапов
- ✅ Аутентификация с паролем
- ✅ Одиночная и пакетная обработка
- ✅ Docker поддержка
- ✅ Конфигурация для всех платформ
- ✅ Подробная документация
- ✅ Безопасность API ключей

## 🎯 Готово к использованию!

Выберите подходящий вариант деплоя и следуйте инструкциям. Все готово для безопасного деплоя!
