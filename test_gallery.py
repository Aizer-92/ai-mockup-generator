#!/usr/bin/env python3
"""
Тест галереи мокапов
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_gallery import get_optimized_gallery
from config import FTP_ENABLED, SERVER_STORAGE_ENABLED

def test_gallery():
    """Тестирует работу галереи"""
    print("🔍 Тестирование галереи мокапов...")
    print(f"FTP_ENABLED: {FTP_ENABLED}")
    print(f"SERVER_STORAGE_ENABLED: {SERVER_STORAGE_ENABLED}")
    
    try:
        gallery = get_optimized_gallery()
        print("✅ Галерея создана успешно")
        
        # Тестируем получение мокапов
        print("\n📁 Получение мокапов...")
        mockups = gallery.get_all_mockups(limit=10)
        print(f"Найдено мокапов: {len(mockups)}")
        
        if mockups:
            print("\n📋 Первые 3 мокапа:")
            for i, mockup in enumerate(mockups[:3]):
                print(f"  {i+1}. {mockup.get('filename', 'N/A')}")
                print(f"     URL: {mockup.get('web_url', 'N/A')}")
                print(f"     Стиль: {mockup.get('style', 'N/A')}")
                print(f"     Нанесение: {mockup.get('application', 'N/A')}")
                print()
        else:
            print("❌ Мокапы не найдены")
            
        # Тестируем фильтры
        print("🔍 Тестирование фильтров...")
        styles, applications = gallery.get_filter_options(mockups)
        print(f"Стили: {styles}")
        print(f"Нанесения: {applications}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gallery()
