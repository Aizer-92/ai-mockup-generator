#!/usr/bin/env python3
"""
Проверка файлов на сервере
"""

import ftplib
import os
from dotenv import load_dotenv

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def check_server_files():
    """Проверяет все файлы на FTP сервере"""
    print("🔍 Проверка файлов на сервере")
    print("============================")
    
    try:
        # Подключаемся к FTP
        ftp = ftplib.FTP()
        ftp.connect(os.getenv('FTP_HOST'), 21)
        ftp.login(os.getenv('FTP_USERNAME'), os.getenv('FTP_PASSWORD'))
        print("✅ FTP подключение успешно")
        
        # Переходим в папку mockups
        ftp.cwd('/public_html/mockups')
        print("✅ Перешли в папку mockups")
        
        # Получаем список файлов
        files = []
        ftp.retrlines('LIST', files.append)
        
        print(f"\n📁 Найдено файлов: {len(files)}")
        
        # Анализируем файлы
        jpg_files = []
        json_files = []
        other_files = []
        
        for file_info in files:
            parts = file_info.split()
            if len(parts) >= 9:
                filename = parts[-1]
                if filename.endswith('.jpg'):
                    jpg_files.append(filename)
                elif filename.endswith('.json'):
                    json_files.append(filename)
                else:
                    other_files.append(filename)
        
        print(f"\n📊 Анализ файлов:")
        print(f"  JPG файлы: {len(jpg_files)}")
        print(f"  JSON файлы: {len(json_files)}")
        print(f"  Другие файлы: {len(other_files)}")
        
        if jpg_files:
            print(f"\n🖼️ JPG файлы:")
            for filename in jpg_files:
                print(f"  {filename}")
        
        if json_files:
            print(f"\n📄 JSON файлы:")
            for filename in json_files:
                print(f"  {filename}")
        
        if other_files:
            print(f"\n📁 Другие файлы:")
            for filename in other_files:
                print(f"  {filename}")
        
        # Проверяем веб-доступ к JPG файлам
        if jpg_files:
            print(f"\n🌐 Проверка веб-доступа:")
            import requests
            for filename in jpg_files[:3]:  # Проверяем первые 3
                url = f"http://search.headcorn.pro/mockups/{filename}"
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        print(f"  ✅ {filename} - доступен")
                    else:
                        print(f"  ❌ {filename} - HTTP {response.status_code}")
                except Exception as e:
                    print(f"  ❌ {filename} - ошибка: {e}")
        
        ftp.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    check_server_files()
