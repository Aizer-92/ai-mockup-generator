#!/usr/bin/env python3
"""
Тест отображения мокапов в галерее
"""

import requests
from PIL import Image
import io
import json
from datetime import datetime

def test_gallery_display():
    """Тестирует отображение мокапов из FTP сервера"""
    print("🔍 Тест отображения мокапов в галерее")
    print("====================================")
    
    # URL тестового файла
    test_url = "http://search.headcorn.pro/mockups/test.txt"
    
    try:
        # Проверяем доступность сервера
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Сервер доступен: {test_url}")
            print(f"   Содержимое: {response.text}")
        else:
            print(f"❌ Сервер недоступен: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False
    
    # Проверяем папку mockups
    mockups_url = "http://search.headcorn.pro/mockups/"
    try:
        response = requests.get(mockups_url, timeout=10)
        print(f"📁 Папка mockups: HTTP {response.status_code}")
        if response.status_code == 200:
            print("   Содержимое папки доступно")
        else:
            print("   Папка недоступна через веб")
    except Exception as e:
        print(f"❌ Ошибка доступа к папке: {e}")
    
    # Проверяем JSON файл
    json_url = "http://search.headcorn.pro/mockups/test_mockup.json"
    try:
        response = requests.get(json_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ JSON файл доступен: {json_url}")
            try:
                data = response.json()
                print(f"   Данные: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except Exception as e:
                print(f"   Ошибка парсинга JSON: {e}")
        else:
            print(f"❌ JSON файл недоступен: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка загрузки JSON: {e}")
    
    print("\n🎯 Рекомендации:")
    print("1. Убедитесь, что Streamlit приложение запущено")
    print("2. Перейдите в 'Галерея мокапов'")
    print("3. Проверьте, что мокапы отображаются корректно")
    print("4. Если есть ошибки, проверьте консоль браузера")
    
    return True

if __name__ == "__main__":
    test_gallery_display()
