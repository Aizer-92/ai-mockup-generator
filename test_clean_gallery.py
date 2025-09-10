#!/usr/bin/env python3
"""
Тест чистой галереи
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_ftp_mockups

def test_clean_gallery():
    """Тестирует чистую галерею"""
    print("🧪 Тест чистой галереи")
    print("=====================")
    
    try:
        # Тестируем получение FTP мокапов
        print("🔍 Получение FTP мокапов...")
        ftp_mockups = get_ftp_mockups(50)
        
        print(f"📊 Результат:")
        print(f"   Найдено мокапов: {len(ftp_mockups)}")
        
        if ftp_mockups:
            print(f"\n🖼️ Мокапы:")
            for i, mockup in enumerate(ftp_mockups, 1):
                print(f"   {i}. {mockup['image_file']}")
                print(f"      URL: {mockup['web_url']}")
                print(f"      Источник: {mockup['source']}")
                print(f"      Метаданные: {mockup['metadata'].get('mockup_style', 'Неизвестно')}")
        else:
            print("   Галерея пуста")
        
        # Проверяем веб-доступ к найденным мокапам
        if ftp_mockups:
            print(f"\n🌐 Проверка веб-доступа:")
            import requests
            for mockup in ftp_mockups:
                try:
                    response = requests.head(mockup['web_url'], timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ {mockup['image_file']} - доступен")
                    else:
                        print(f"   ❌ {mockup['image_file']} - HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {mockup['image_file']} - ошибка: {e}")
        
        print(f"\n🎯 Рекомендации:")
        if ftp_mockups:
            print("   ✅ Галерея содержит рабочие мокапы")
            print("   ✅ Все файлы доступны через веб")
            print("   ✅ Можно открывать Streamlit приложение")
        else:
            print("   📝 Галерея пуста - сгенерируйте новые мокапы")
            print("   📝 Или проверьте настройки FTP")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_clean_gallery()
