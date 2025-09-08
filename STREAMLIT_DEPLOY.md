# Деплой на Streamlit Cloud

## Быстрый старт

1. **Перейдите на [share.streamlit.io](https://share.streamlit.io)**
2. **Войдите через GitHub**
3. **Нажмите "New app"**
4. **Выберите репозиторий**: `Aizer-92/ai-mockup-generator`
5. **Укажите ветку**: `main`
6. **Укажите главный файл**: `main.py`

## Настройка секретов

После создания приложения:

1. **Перейдите в Settings → Secrets**
2. **Добавьте следующие секреты**:

```toml
GEMINI_API_KEY = "AIzaSyCIfsGnKDfI1UedKQRzzrOA0v1oPWc7tIs"
AUTH_ENABLED = "true"
AUTH_PASSWORD = "your_secure_password_here"
```

## Преимущества Streamlit Cloud

✅ **Простота**: Автоматический деплой из GitHub  
✅ **Бесплатно**: Для публичных репозиториев  
✅ **Автообновления**: При каждом push в main  
✅ **Секреты**: Безопасное хранение API ключей  
✅ **Логи**: Встроенная система логирования  

## Структура проекта

```
├── main.py                    # Главный файл приложения
├── config.py                  # Конфигурация (поддерживает secrets)
├── auth.py                    # Система аутентификации
├── mockup_generator.py        # Основная логика генерации
├── gemini_client.py           # Клиент для Gemini API
├── image_processor.py         # Обработка изображений
├── requirements.txt           # Зависимости Python
├── .streamlit/
│   ├── config.toml           # Конфигурация Streamlit
│   └── secrets.toml.example  # Пример секретов
└── README.md                 # Документация
```

## Локальная разработка

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

# Создайте .env файл
cp .streamlit/secrets.toml.example .env
# Отредактируйте .env с вашими ключами

# Запустите приложение
streamlit run main.py
```

## Troubleshooting

### Проблема с OpenCV
Если возникают ошибки с OpenCV, убедитесь, что в requirements.txt указана правильная версия:
```
opencv-python-headless>=4.8.0
```

### Проблема с аутентификацией
Проверьте, что секреты правильно настроены в Streamlit Cloud.

### Проблема с API ключом
Убедитесь, что GEMINI_API_KEY правильно указан в секретах.
