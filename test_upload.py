#!/usr/bin/env python3
"""
Тест загрузки файла на FTP сервер
"""

import ftplib
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def test_upload():
    """Тестирует загрузку файла на FTP сервер"""
    print("🚀 Тест загрузки файла на FTP сервер")
    print("=====================================")
    
    try:
        # Подключаемся к FTP
        ftp = ftplib.FTP()
        ftp.connect(os.getenv('FTP_HOST'), 21)
        ftp.login(os.getenv('FTP_USERNAME'), os.getenv('FTP_PASSWORD'))
        print("✅ FTP подключение успешно")
        
        # Переходим в папку mockups
        ftp.cwd('/public_html/mockups')
        print("✅ Перешли в папку mockups")
        
        # Создаем тестовый JSON файл
        test_data = {
            "filename": "test_mockup.jpg",
            "metadata": {
                "mockup_style": "Тестовый стиль",
                "logo_application": "Тестовое нанесение",
                "logo_placement": "Центр",
                "test": True
            },
            "created_at": datetime.now().isoformat(),
            "source": "ftp_test"
        }
        
        # Загружаем JSON файл
        json_filename = "test_mockup.json"
        json_data = json.dumps(test_data, ensure_ascii=False, indent=2)
        
        # Загружаем файл
        from io import BytesIO
        json_buffer = BytesIO(json_data.encode('utf-8'))
        ftp.storbinary(f'STOR {json_filename}', json_buffer)
        print(f"✅ Файл {json_filename} загружен")
        
        # Создаем тестовый текстовый файл
        text_filename = "test.txt"
        text_data = "Это тестовый файл для проверки веб-доступа"
        text_buffer = BytesIO(text_data.encode('utf-8'))
        ftp.storbinary(f'STOR {text_filename}', text_buffer)
        print(f"✅ Файл {text_filename} загружен")
        
        # Показываем содержимое папки
        print("\n📁 Содержимое папки mockups:")
        contents = []
        ftp.retrlines('LIST', contents.append)
        
        for item in contents:
            print(f"  {item}")
        
        ftp.quit()
        
        # Проверяем веб-доступ
        print("\n🌐 Проверка веб-доступа:")
        import urllib.request
        try:
            response = urllib.request.urlopen('http://search.headcorn.pro/mockups/test.txt')
            content = response.read().decode('utf-8')
            print(f"✅ Веб-доступ работает: {content}")
        except Exception as e:
            print(f"❌ Веб-доступ не работает: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_upload()
