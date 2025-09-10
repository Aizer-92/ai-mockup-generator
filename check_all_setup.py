#!/usr/bin/env python3
"""
Проверка всех настроек приложения
"""
import os
import sys

def check_basic_config():
    """Проверяет базовую конфигурацию"""
    print("🔍 Проверка базовой конфигурации...")
    
    try:
        from config import GEMINI_API_KEY, AUTH_ENABLED, AUTH_PASSWORD
        
        if GEMINI_API_KEY:
            print("✅ GEMINI_API_KEY настроен")
        else:
            print("❌ GEMINI_API_KEY не настроен")
            return False
        
        if AUTH_ENABLED:
            print("✅ Аутентификация включена")
        else:
            print("⚠️ Аутентификация отключена")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def check_google_drive():
    """Проверяет настройки Google Drive"""
    print("\n🔍 Проверка Google Drive...")
    
    try:
        from config import GOOGLE_DRIVE_ENABLED
        
        if GOOGLE_DRIVE_ENABLED:
            print("✅ Google Drive включен")
            
            # Проверяем credentials
            if os.path.exists('credentials.json'):
                print("✅ credentials.json найден")
            else:
                print("❌ credentials.json не найден")
                return False
        else:
            print("⚠️ Google Drive отключен")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка Google Drive: {e}")
        return False

def check_ftp():
    """Проверяет настройки FTP"""
    print("\n🔍 Проверка FTP...")
    
    try:
        from config import FTP_ENABLED, FTP_HOST, FTP_USERNAME, FTP_PASSWORD
        
        if FTP_ENABLED:
            print("✅ FTP включен")
            
            if FTP_HOST and FTP_USERNAME and FTP_PASSWORD:
                print("✅ FTP настройки заполнены")
                
                # Тестируем подключение
                from ftp_uploader import get_ftp_uploader
                uploader = get_ftp_uploader()
                
                if uploader:
                    print("✅ FTP подключение работает")
                else:
                    print("❌ FTP подключение не работает")
                    return False
            else:
                print("❌ FTP настройки не заполнены")
                return False
        else:
            print("⚠️ FTP отключен")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка FTP: {e}")
        return False

def check_server_storage():
    """Проверяет настройки серверного хранилища"""
    print("\n🔍 Проверка серверного хранилища...")
    
    try:
        from config import SERVER_STORAGE_ENABLED
        
        if SERVER_STORAGE_ENABLED:
            print("✅ Серверное хранилище включено")
        else:
            print("⚠️ Серверное хранилище отключено")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка серверного хранилища: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка настроек AI Mockup Generator")
    print("=" * 50)
    
    # Проверяем все компоненты
    basic_ok = check_basic_config()
    google_ok = check_google_drive()
    ftp_ok = check_ftp()
    server_ok = check_server_storage()
    
    print("\n" + "=" * 50)
    print("📋 РЕЗУЛЬТАТ ПРОВЕРКИ")
    print("=" * 50)
    
    if basic_ok and (google_ok or ftp_ok or server_ok):
        print("🎉 Все готово! Приложение настроено корректно")
        print("✅ Можете запускать: streamlit run main.py")
        
        # Показываем активные хранилища
        print("\n📁 Активные хранилища:")
        if google_ok:
            print("   - Google Drive")
        if ftp_ok:
            print("   - FTP сервер")
        if server_ok:
            print("   - Локальное хранилище")
        
        sys.exit(0)
    else:
        print("❌ Нужна настройка")
        print("📝 Следуйте инструкциям:")
        
        if not basic_ok:
            print("   - Настройте базовую конфигурацию")
        if not google_ok and not ftp_ok and not server_ok:
            print("   - Настройте хотя бы одно хранилище")
        
        print("\n🔗 Полезные ссылки:")
        print("   Google Drive: STREAMLIT_GOOGLE_DRIVE_SETUP.md")
        print("   FTP сервер: STREAMLIT_FTP_SETUP.md")
        print("   Локальное: SERVER_STORAGE_OPTIONS.md")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
