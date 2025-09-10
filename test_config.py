#!/usr/bin/env python3
"""
Тест конфигурации
"""

from config import *

def test_config():
    """Тестирует загрузку конфигурации"""
    print("🔍 Тест конфигурации")
    print("===================")
    
    print(f"FTP_ENABLED: {FTP_ENABLED}")
    print(f"FTP_HOST: {FTP_HOST}")
    print(f"FTP_USERNAME: {FTP_USERNAME}")
    print(f"FTP_PASSWORD: {'*' * len(FTP_PASSWORD) if FTP_PASSWORD else 'НЕ УСТАНОВЛЕН'}")
    print(f"FTP_REMOTE_PATH: {FTP_REMOTE_PATH}")
    print(f"SERVER_WEB_URL: {SERVER_WEB_URL}")
    
    print(f"\nGOOGLE_DRIVE_ENABLED: {GOOGLE_DRIVE_ENABLED}")
    print(f"SERVER_STORAGE_ENABLED: {SERVER_STORAGE_ENABLED}")
    
    # Проверяем FTP загрузчик
    try:
        from ftp_uploader import get_ftp_uploader
        uploader = get_ftp_uploader()
        if uploader:
            print("\n✅ FTP загрузчик инициализирован успешно")
        else:
            print("\n❌ FTP загрузчик не инициализирован")
    except Exception as e:
        print(f"\n❌ Ошибка FTP загрузчика: {e}")

if __name__ == "__main__":
    test_config()
