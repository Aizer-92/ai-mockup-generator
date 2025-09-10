#!/usr/bin/env python3
"""
Тест FTP мокапов без Streamlit
"""

from ftp_uploader import get_ftp_uploader
import requests

def test_ftp_mockups():
    """Тестирует FTP мокапы"""
    print("🧪 Тест FTP мокапов")
    print("===================")
    
    try:
        # Получаем FTP загрузчик
        uploader = get_ftp_uploader()
        if not uploader:
            print("❌ Не удалось создать FTP загрузчик")
            return False
        
        # Получаем список мокапов
        print("🔍 Получение списка мокапов...")
        mockups = uploader.list_files()
        
        print(f"📊 Найдено мокапов: {len(mockups)}")
        
        if not mockups:
            print("📝 Галерея пуста")
            return True
        
        # Проверяем каждый мокап
        working_mockups = []
        broken_mockups = []
        
        print(f"\n🌐 Проверка веб-доступа:")
        for mockup in mockups:
            filename = mockup['filename']
            web_url = mockup['web_url']
            
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.head(web_url, timeout=5, headers=headers)
                if response.status_code == 200:
                    print(f"   ✅ {filename} - доступен")
                    working_mockups.append(mockup)
                else:
                    print(f"   ❌ {filename} - HTTP {response.status_code}")
                    broken_mockups.append(mockup)
            except Exception as e:
                print(f"   ❌ {filename} - ошибка: {e}")
                broken_mockups.append(mockup)
        
        print(f"\n📊 Результат:")
        print(f"   Рабочих мокапов: {len(working_mockups)}")
        print(f"   Сломанных мокапов: {len(broken_mockups)}")
        
        if working_mockups:
            print(f"\n✅ Рабочие мокапы:")
            for mockup in working_mockups:
                print(f"   - {mockup['filename']}")
                print(f"     URL: {mockup['web_url']}")
                print(f"     Стиль: {mockup['metadata'].get('mockup_style', 'Неизвестно')}")
        
        if broken_mockups:
            print(f"\n❌ Сломанные мокапы:")
            for mockup in broken_mockups:
                print(f"   - {mockup['filename']}")
        
        print(f"\n🎯 Рекомендации:")
        if working_mockups:
            print("   ✅ Галерея содержит рабочие мокапы")
            print("   ✅ Можно открывать Streamlit приложение")
        else:
            print("   📝 Нет рабочих мокапов")
            print("   📝 Сгенерируйте новые мокапы")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    test_ftp_mockups()
