# 🖥️ Варианты хранения мокапов на сервере

## Обзор

Вместо Google Drive можно использовать ваш собственный сервер для хранения мокапов. Это проще, быстрее и не требует настройки OAuth.

## 🎯 Варианты реализации

### 1. 📁 Локальная файловая система (рекомендуется)

#### Преимущества:
- ✅ **Простота** - никаких API ключей
- ✅ **Скорость** - мгновенный доступ к файлам
- ✅ **Надежность** - полный контроль
- ✅ **Бесплатно** - нет лимитов API

#### Реализация:
```python
# В config.py
LOCAL_STORAGE_ENABLED = True
STORAGE_PATH = '/path/to/mockups'  # Путь на сервере

# В main.py
def save_mockup_locally(image_data, metadata):
    os.makedirs(STORAGE_PATH, exist_ok=True)
    filename = f"mockup_{timestamp}.jpg"
    filepath = os.path.join(STORAGE_PATH, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_data)
    
    # Сохраняем метаданные
    metadata_file = filepath.replace('.jpg', '.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
```

### 2. 🌐 HTTP API на вашем сервере

#### Преимущества:
- ✅ **Централизованное хранение**
- ✅ **Доступ из любого места**
- ✅ **Масштабируемость**
- ✅ **Резервное копирование**

#### Реализация:
```python
# Простой Flask API на сервере
from flask import Flask, request, jsonify, send_file
import os
import json

app = Flask(__name__)
UPLOAD_FOLDER = '/var/www/mockups'

@app.route('/upload', methods=['POST'])
def upload_mockup():
    file = request.files['image']
    metadata = request.form.get('metadata')
    
    filename = f"mockup_{int(time.time())}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(filepath)
    
    # Сохраняем метаданные
    with open(filepath.replace('.jpg', '.json'), 'w') as f:
        json.dump(json.loads(metadata), f)
    
    return jsonify({'status': 'success', 'filename': filename})

@app.route('/list', methods=['GET'])
def list_mockups():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.jpg'):
            files.append({
                'filename': filename,
                'path': f'/download/{filename}',
                'created': os.path.getctime(os.path.join(UPLOAD_FOLDER, filename))
            })
    return jsonify(files)

@app.route('/download/<filename>')
def download_mockup(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))
```

### 3. 🗄️ База данных с файлами

#### Преимущества:
- ✅ **Структурированное хранение**
- ✅ **Быстрый поиск**
- ✅ **Метаданные в БД**
- ✅ **Версионность**

#### Реализация:
```python
# SQLite база данных
import sqlite3
import base64

def save_mockup_to_db(image_data, metadata):
    conn = sqlite3.connect('mockups.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mockups (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            image_data BLOB,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO mockups (filename, image_data, metadata)
        VALUES (?, ?, ?)
    ''', (filename, image_data, json.dumps(metadata)))
    
    conn.commit()
    conn.close()
```

## 🚀 Рекомендуемое решение

### Вариант 1: Простая файловая система

```python
# config.py
LOCAL_STORAGE_ENABLED = True
STORAGE_PATH = '/var/www/mockups'  # Путь на вашем сервере
WEB_URL = 'https://your-server.com/mockups'  # URL для доступа

# main.py
def save_mockup_to_server(image_data, metadata):
    if not LOCAL_STORAGE_ENABLED:
        return
    
    # Создаем папку если не существует
    os.makedirs(STORAGE_PATH, exist_ok=True)
    
    # Генерируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    style = metadata.get("mockup_style", "unknown")
    filename = f"mockup_{timestamp}_{style}.jpg"
    
    # Сохраняем изображение
    filepath = os.path.join(STORAGE_PATH, filename)
    with open(filepath, 'wb') as f:
        f.write(image_data)
    
    # Сохраняем метаданные
    metadata_file = filepath.replace('.jpg', '.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Мокап сохранен: {filepath}")
    return filename

def get_mockups_from_server():
    if not LOCAL_STORAGE_ENABLED:
        return []
    
    mockups = []
    if os.path.exists(STORAGE_PATH):
        for filename in os.listdir(STORAGE_PATH):
            if filename.endswith('.jpg'):
                filepath = os.path.join(STORAGE_PATH, filename)
                metadata_file = filepath.replace('.jpg', '.json')
                
                # Загружаем метаданные
                metadata = {}
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                
                mockups.append({
                    'filename': filename,
                    'filepath': filepath,
                    'web_url': f"{WEB_URL}/{filename}",
                    'metadata': metadata,
                    'created_time': os.path.getctime(filepath)
                })
    
    return sorted(mockups, key=lambda x: x['created_time'], reverse=True)
```

### Настройка веб-сервера

#### Nginx конфигурация:
```nginx
server {
    listen 80;
    server_name your-server.com;
    
    location /mockups/ {
        alias /var/www/mockups/;
        autoindex on;
        add_header Access-Control-Allow-Origin *;
    }
}
```

#### Apache конфигурация:
```apache
<VirtualHost *:80>
    ServerName your-server.com
    DocumentRoot /var/www
    
    <Directory "/var/www/mockups">
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

## 🔧 Настройка для Streamlit Cloud

### Вариант 1: Временное хранилище
```python
# Используем /tmp папку в Streamlit Cloud
STORAGE_PATH = '/tmp/mockups'
```

### Вариант 2: Внешний API
```python
# Отправляем на ваш сервер
SERVER_API_URL = 'https://your-server.com/api/mockups'

def upload_to_server(image_data, metadata):
    files = {'image': ('mockup.jpg', image_data, 'image/jpeg')}
    data = {'metadata': json.dumps(metadata)}
    
    response = requests.post(f"{SERVER_API_URL}/upload", files=files, data=data)
    return response.json()
```

## 📊 Сравнение вариантов

| Вариант | Сложность | Скорость | Надежность | Стоимость |
|---------|-----------|----------|------------|-----------|
| Google Drive | Высокая | Средняя | Высокая | Бесплатно |
| Локальная ФС | Низкая | Высокая | Средняя | Бесплатно |
| HTTP API | Средняя | Высокая | Высокая | Бесплатно |
| База данных | Средняя | Высокая | Высокая | Бесплатно |

## 🎯 Рекомендация

**Для вашего случая рекомендую:**

1. **Локальная файловая система** - самый простой вариант
2. **Настройка веб-сервера** для доступа к файлам
3. **Резервное копирование** на другой сервер

Это даст вам:
- ✅ Простоту настройки
- ✅ Высокую скорость
- ✅ Полный контроль
- ✅ Отсутствие лимитов API

Хотите, чтобы я реализовал этот вариант?
