#!/usr/bin/env python3
"""
Проверка URL от FTP загрузчика
"""

from ftp_uploader import get_ftp_uploader

def check_ftp_urls():
    """Проверяет URL от FTP загрузчика"""
    print("🔍 Проверка URL от FTP загрузчика")
    print("=================================")
    
    try:
        # Получаем FTP загрузчик
        uploader = get_ftp_uploader()
        if not uploader:
            print("❌ Не удалось создать FTP загрузчик")
            return False
        
        print(f"FTP загрузчик:")
        print(f"  Host: {uploader.host}")
        print(f"  Remote path: {uploader.remote_path}")
        print(f"  Web URL: {uploader.web_url}")
        
        # Получаем список мокапов
        mockups = uploader.list_files()
        
        print(f"\n📊 Найдено мокапов: {len(mockups)}")
        
        for mockup in mockups:
            print(f"\nМокап: {mockup['filename']}")
            print(f"  Web URL: {mockup['web_url']}")
            print(f"  Метаданные: {mockup['metadata']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    check_ftp_urls()
