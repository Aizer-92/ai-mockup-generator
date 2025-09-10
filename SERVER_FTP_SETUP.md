# 🖥️ Настройка серверного хранилища через FTP

## Информация о сервере

- **FTP Host**: search.headcorn.pro
- **Username**: victoruk_search
- **Password**: L2F&A#3zVpCq*T
- **Web URL**: http://search.headcorn.pro/

## 🚀 Быстрая настройка

### 1. Создайте папку для мокапов на сервере

```bash
# Подключитесь к FTP
ftp search.headcorn.pro
# Username: victoruk_search
# Password: L2F&A#3zVpCq*T

# Создайте папку
mkdir mockups
cd mockups
mkdir static
```

### 2. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Основные настройки
GEMINI_API_KEY=your_gemini_api_key_here
AUTH_ENABLED=true
AUTH_PASSWORD=your_password_here

# Серверное хранилище (включено по умолчанию)
SERVER_STORAGE_ENABLED=true
SERVER_STORAGE_PATH=mockups
SERVER_WEB_URL=http://search.headcorn.pro/mockups

# Google Drive (отключено)
GOOGLE_DRIVE_ENABLED=false
```

### 3. Настройте веб-сервер

#### Apache конфигурация:
```apache
<VirtualHost *:80>
    ServerName search.headcorn.pro
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
    server_name search.headcorn.pro;
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

## 🔧 Реализация FTP загрузки

### Создайте модуль для FTP загрузки:

```python
# ftp_uploader.py
import ftplib
import os
import json
from datetime import datetime

class FTPUploader:
    def __init__(self, host, username, password, remote_path="/mockups"):
        self.host = host
        self.username = username
        self.password = password
        self.remote_path = remote_path
    
    def upload_file(self, local_file, remote_file):
        """Загружает файл на FTP сервер"""
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                ftp.cwd(self.remote_path)
                
                with open(local_file, 'rb') as file:
                    ftp.storbinary(f'STOR {remote_file}', file)
                
                print(f"✅ Файл загружен: {remote_file}")
                return True
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
    
    def list_files(self):
        """Получает список файлов с сервера"""
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                ftp.cwd(self.remote_path)
                
                files = []
                ftp.retrlines('LIST', files.append)
                return files
        except Exception as e:
            print(f"❌ Ошибка получения списка: {e}")
            return []
```

## 📁 Структура папок на сервере

```
/var/www/html/
├── mockups/                 # Основная папка для мокапов
│   ├── static/             # Статические файлы
│   ├── mockup_20241210_143022_luxury.jpg
│   ├── mockup_20241210_143022_luxury.json
│   ├── mockup_20241210_143125_minimal.jpg
│   └── mockup_20241210_143125_minimal.json
└── index.html              # Главная страница
```

## 🎯 Преимущества серверного хранилища

### ✅ Простота:
- Никаких API ключей
- Никаких OAuth настроек
- Простая FTP загрузка

### ✅ Скорость:
- Мгновенный доступ к файлам
- Нет лимитов API
- Локальная сеть

### ✅ Контроль:
- Полный контроль над файлами
- Резервное копирование
- Настройка прав доступа

### ✅ Стоимость:
- Бесплатно
- Нет лимитов на количество файлов
- Нет лимитов на размер

## 🔧 Настройка для Streamlit Cloud

### Вариант 1: Временное хранилище
```python
# Используем /tmp папку в Streamlit Cloud
SERVER_STORAGE_PATH = '/tmp/mockups'
SERVER_WEB_URL = 'https://your-streamlit-app.streamlit.app/static/mockups'
```

### Вариант 2: FTP загрузка
```python
# Загружаем на ваш сервер через FTP
FTP_HOST = 'search.headcorn.pro'
FTP_USERNAME = 'victoruk_search'
FTP_PASSWORD = 'L2F&A#3zVpCq*T'
FTP_REMOTE_PATH = '/mockups'
```

## 🧪 Тестирование

### 1. Проверьте FTP подключение:
```python
import ftplib

try:
    with ftplib.FTP('search.headcorn.pro') as ftp:
        ftp.login('victoruk_search', 'L2F&A#3zVpCq*T')
        print("✅ FTP подключение успешно")
        ftp.retrlines('LIST')
except Exception as e:
    print(f"❌ Ошибка FTP: {e}")
```

### 2. Проверьте веб-доступ:
```bash
curl http://search.headcorn.pro/mockups/
```

### 3. Запустите приложение:
```bash
streamlit run main.py
```

## 📋 Чек-лист настройки

- [ ] FTP подключение работает
- [ ] Папка `/mockups` создана на сервере
- [ ] Веб-сервер настроен для доступа к папке
- [ ] Переменные окружения настроены
- [ ] Приложение загружает файлы на сервер
- [ ] Галерея отображает файлы с сервера
- [ ] Веб-доступ к файлам работает

## 🎉 Готово!

После настройки:
- ✅ Все мокапы автоматически загружаются на ваш сервер
- ✅ Галерея отображает мокапы с сервера
- ✅ Файлы доступны по URL: `http://search.headcorn.pro/mockups/`
- ✅ Полный контроль над хранилищем
- ✅ Никаких лимитов API

## 🔗 Полезные ссылки

- **FTP клиент**: FileZilla, WinSCP
- **Веб-интерфейс**: http://search.headcorn.pro/mockups/
- **SSH доступ**: для настройки веб-сервера
