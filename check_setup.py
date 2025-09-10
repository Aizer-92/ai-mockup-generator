#!/usr/bin/env python3
"""
Быстрая проверка настройки Google Drive для Streamlit
"""
import os
import json

def check_credentials():
    """Проверяет файл credentials.json"""
    print("🔍 Проверка credentials.json...")
    
    if not os.path.exists('credentials.json'):
        print("❌ Файл credentials.json не найден!")
        print("📝 Скачайте файл из Google Cloud Console")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds:
            print("✅ Desktop Application credentials найдены")
            print(f"🆔 Client ID: {creds['installed']['client_id']}")
            return True
        else:
            print("❌ Неверный формат credentials.json")
            print("📝 Убедитесь, что скачали Desktop Application credentials")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")
        return False

def check_env():
    """Проверяет переменные окружения"""
    print("\n🔍 Проверка переменных окружения...")
    
    # Проверяем .env файл
    if os.path.exists('.env'):
        print("✅ Файл .env найден")
        with open('.env', 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                print("✅ GEMINI_API_KEY настроен")
            else:
                print("❌ GEMINI_API_KEY не найден в .env")
            
            if 'GOOGLE_DRIVE_ENABLED=true' in content:
                print("✅ GOOGLE_DRIVE_ENABLED=true")
            else:
                print("⚠️ GOOGLE_DRIVE_ENABLED не установлен в true")
    else:
        print("❌ Файл .env не найден")
        print("📝 Создайте файл .env с переменными окружения")

def check_requirements():
    """Проверяет зависимости"""
    print("\n🔍 Проверка зависимостей...")
    
    try:
        import streamlit
        print("✅ Streamlit установлен")
    except ImportError:
        print("❌ Streamlit не установлен")
        print("📝 Запустите: pip install -r requirements.txt")
    
    try:
        import google.auth
        print("✅ Google Auth установлен")
    except ImportError:
        print("❌ Google Auth не установлен")
        print("📝 Запустите: pip install -r requirements.txt")
    
    try:
        from googleapiclient.discovery import build
        print("✅ Google API Client установлен")
    except ImportError:
        print("❌ Google API Client не установлен")
        print("📝 Запустите: pip install -r requirements.txt")

def check_token():
    """Проверяет токен доступа"""
    print("\n🔍 Проверка токена доступа...")
    
    if os.path.exists('token.json'):
        print("✅ Токен доступа найден")
        print("🎉 Google Drive уже настроен!")
        return True
    else:
        print("⚠️ Токен доступа не найден")
        print("📝 Выполните первую авторизацию при запуске приложения")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 Проверка настройки Google Drive для Streamlit")
    print("=" * 50)
    
    # Проверяем все компоненты
    creds_ok = check_credentials()
    check_env()
    check_requirements()
    token_ok = check_token()
    
    print("\n" + "=" * 50)
    print("📋 РЕЗУЛЬТАТ ПРОВЕРКИ")
    print("=" * 50)
    
    if creds_ok and token_ok:
        print("🎉 Все готово! Google Drive настроен корректно")
        print("✅ Можете запускать: streamlit run main.py")
    elif creds_ok:
        print("⚠️ Credentials настроены, но нужна авторизация")
        print("✅ Запустите: streamlit run main.py")
        print("📝 Выполните авторизацию в браузере")
    else:
        print("❌ Нужна настройка Google Cloud Console")
        print("📝 Следуйте инструкции в STREAMLIT_GOOGLE_DRIVE_SETUP.md")
    
    print("\n🔗 Полезные ссылки:")
    print("   Google Cloud Console: https://console.cloud.google.com/")
    print("   Инструкция: STREAMLIT_GOOGLE_DRIVE_SETUP.md")

if __name__ == "__main__":
    main()
