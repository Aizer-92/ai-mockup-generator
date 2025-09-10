# 🚀 Настройка FTP для Streamlit Cloud

## Обзор

Эта инструкция поможет настроить загрузку мокапов на ваш FTP сервер из Streamlit приложения.

## 🔧 Настройка

### 1. Добавьте FTP настройки в Streamlit Secrets

В настройках вашего Streamlit приложения (Settings → Secrets) добавьте:

```toml
# Основные настройки
GEMINI_API_KEY = "your_gemini_api_key_here"
AUTH_ENABLED = true
AUTH_PASSWORD = "your_password_here"

# Google Drive (отключено)
GOOGLE_DRIVE_ENABLED = false

# Серверное хранилище (отключено для Streamlit Cloud)
SERVER_STORAGE_ENABLED = false

# FTP настройки (ваш сервер)
FTP_ENABLED = true
FTP_HOST = "your_ftp_host_here"
FTP_USERNAME = "your_ftp_username_here"
FTP_PASSWORD = "your_ftp_password_here"
FTP_REMOTE_PATH = "/mockups"
```

### 2. Настройте веб-сервер на вашем сервере

#### Apache конфигурация:
```apache
<VirtualHost *:80>
    ServerName your_domain.com
    DocumentRoot /var/www/html
    
    # Папка для мокапов
    Alias /mockups /var/www/html/mockups
    <Directory "/var/www/html/mockups">
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
        
        # Разрешаем CORS для Streamlit
        Header always set Access-Control-Allow-Origin "*"
        Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
        Header always set Access-Control-Allow-Headers "Content-Type"
    </Directory>
</VirtualHost>
```

#### Nginx конфигурация:
```nginx
server {
    listen 80;
    server_name your_domain.com;
    root /var/www/html;
    
    location /mockups/ {
        alias /var/www/html/mockups/;
        autoindex on;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";
    }
}
```

### 3. Создайте папку для мокапов

```bash
# Подключитесь к серверу по SSH
ssh user@your_server

# Создайте папку
mkdir -p /var/www/html/mockups
chmod 755 /var/www/html/mockups

# Проверьте права доступа
ls -la /var/www/html/mockups
```

## 🧪 Тестирование

### 1. Проверьте FTP подключение

Создайте тестовый скрипт:

```python
# test_ftp_connection.py
import ftplib

def test_ftp():
    try:
        with ftplib.FTP('your_ftp_host') as ftp:
            ftp.login('your_username', 'your_password')
            print("✅ FTP подключение успешно")
            
            # Создайте папку если не существует
            try:
                ftp.cwd('/mockups')
            except ftplib.error_perm:
                ftp.mkd('/mockups')
                print("✅ Папка /mockups создана")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка FTP: {e}")
        return False

if __name__ == "__main__":
    test_ftp()
```

### 2. Проверьте веб-доступ

```bash
curl http://your_domain.com/mockups/
```

### 3. Запустите Streamlit приложение

```bash
streamlit run main.py
```

## 📁 Структура файлов на сервере

```
/var/www/html/mockups/
├── mockup_20241210_143022_luxury.jpg
├── mockup_20241210_143022_luxury.json
├── mockup_20241210_143125_minimal.jpg
├── mockup_20241210_143125_minimal.json
└── ...
```

## 🎯 Как это работает

### 1. Генерация мокапа
- Пользователь загружает изображение товара и логотип
- AI генерирует мокап
- Мокап сохраняется в памяти сессии

### 2. Загрузка на FTP
- Мокап автоматически загружается на ваш FTP сервер
- Создается JSON файл с метаданными
- Файлы доступны по URL: `http://your_domain.com/mockups/`

### 3. Отображение в галерее
- Галерея загружает список файлов с FTP сервера
- Отображает мокапы с метаданными
- Показывает прямые ссылки на файлы

## 🔒 Безопасность

### FTP настройки:
- Используйте сильные пароли
- Ограничьте доступ по IP если возможно
- Регулярно меняйте пароли

### Веб-сервер:
- Настройте HTTPS если возможно
- Ограничьте доступ к папке /mockups
- Настройте резервное копирование

## 📊 Преимущества

### ✅ Простота:
- Никаких API ключей
- Никаких OAuth настроек
- Простая FTP загрузка

### ✅ Скорость:
- Мгновенный доступ к файлам
- Нет лимитов API
- Прямая загрузка на сервер

### ✅ Контроль:
- Полный контроль над файлами
- Резервное копирование
- Настройка прав доступа

### ✅ Стоимость:
- Бесплатно
- Нет лимитов на количество файлов
- Нет лимитов на размер

## 🚨 Устранение неполадок

### Ошибка "FTP настройки не заполнены"
- Проверьте, что все FTP переменные добавлены в Streamlit Secrets
- Убедитесь, что переменные имеют правильные значения

### Ошибка "FTP подключение не удалось"
- Проверьте правильность FTP данных
- Убедитесь, что сервер доступен
- Проверьте файрвол и сетевые настройки

### Ошибка "Папка не найдена"
- Создайте папку /mockups на сервере
- Проверьте права доступа FTP пользователя

### Файлы не отображаются в галерее
- Проверьте веб-доступ к папке /mockups
- Убедитесь, что CORS настроен правильно
- Проверьте права доступа к файлам

## 📋 Чек-лист настройки

- [ ] FTP настройки добавлены в Streamlit Secrets
- [ ] Папка /mockups создана на сервере
- [ ] Веб-сервер настроен для доступа к папке
- [ ] CORS настроен для Streamlit
- [ ] FTP подключение работает
- [ ] Веб-доступ к файлам работает
- [ ] Приложение загружает файлы на сервер
- [ ] Галерея отображает файлы с сервера

## 🎉 Готово!

После настройки:
- ✅ Все мокапы автоматически загружаются на ваш сервер
- ✅ Галерея отображает мокапы с сервера
- ✅ Файлы доступны по URL: `http://your_domain.com/mockups/`
- ✅ Полный контроль над хранилищем
- ✅ Никаких лимитов API

## 🔗 Полезные ссылки

- **Streamlit Secrets**: https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management
- **FTP клиент**: FileZilla, WinSCP
- **Веб-интерфейс**: http://your_domain.com/mockups/
