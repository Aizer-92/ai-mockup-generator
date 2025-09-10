#!/usr/bin/env python3
"""
Скрипт для настройки Google Drive API
Помогает определить правильные настройки для Google Cloud Console
"""
import os
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

def check_credentials_file():
    """Проверяет файл credentials.json"""
    print("🔍 Проверка файла credentials.json...")
    
    if not os.path.exists('credentials.json'):
        print("❌ Файл credentials.json не найден!")
        print("📝 Скачайте файл credentials.json из Google Cloud Console")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        print("✅ Файл credentials.json найден")
        
        # Определяем тип credentials
        if 'installed' in creds_data:
            print("📱 Тип: Desktop Application")
            client_id = creds_data['installed']['client_id']
            print(f"🆔 Client ID: {client_id}")
            return 'desktop'
        elif 'web' in creds_data:
            print("🌐 Тип: Web Application")
            client_id = creds_data['web']['client_id']
            print(f"🆔 Client ID: {client_id}")
            return 'web'
        else:
            print("❌ Неизвестный формат credentials.json")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения credentials.json: {e}")
        return False

def show_google_cloud_setup():
    """Показывает инструкции по настройке Google Cloud Console"""
    print("\n" + "="*60)
    print("🔧 НАСТРОЙКА GOOGLE CLOUD CONSOLE")
    print("="*60)
    
    print("\n1. 📋 Перейдите в Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. 🎯 Выберите проект:")
    print("   quickstart-1591698112539")
    
    print("\n3. 🔑 Перейдите в Credentials:")
    print("   APIs & Services → Credentials")
    
    print("\n4. ✏️ Найдите и отредактируйте OAuth 2.0 Client ID:")
    print("   1047954485208-849n8mrie4rrapktqodrg6mp4js9r0oi.apps.googleusercontent.com")
    
    print("\n5. 🌐 Добавьте Authorized redirect URIs:")
    print("   Для Desktop Application:")
    print("   - http://localhost:8080")
    print("   - http://localhost:8081")
    print("   - http://localhost:8082")
    print("   - http://localhost:8083")
    print("   - http://localhost:8084")
    print("   - http://localhost:8085")
    print("   - http://localhost:8086")
    print("   - http://localhost:8087")
    print("   - http://localhost:8088")
    print("   - http://localhost:8089")
    print("   - http://localhost:8090")
    
    print("\n   Или добавьте диапазон портов:")
    print("   - http://localhost:61463-61500")
    
    print("\n6. 💾 Сохраните изменения")
    
    print("\n7. ⏱️ Подождите 1-2 минуты для применения изменений")

def show_oauth_consent_setup():
    """Показывает инструкции по настройке OAuth consent screen"""
    print("\n" + "="*60)
    print("🔐 НАСТРОЙКА OAUTH CONSENT SCREEN")
    print("="*60)
    
    print("\n1. 📋 Перейдите в OAuth consent screen:")
    print("   APIs & Services → OAuth consent screen")
    
    print("\n2. 👤 User Type: External")
    
    print("\n3. 📝 Заполните обязательные поля:")
    print("   - App name: AI Mockup Generator")
    print("   - User support email: ваш email")
    print("   - Developer contact: ваш email")
    
    print("\n4. 🔑 Добавьте Scopes:")
    print("   - https://www.googleapis.com/auth/drive.file")
    
    print("\n5. 👥 Добавьте Test users:")
    print("   - ваш email")
    
    print("\n6. 💾 Сохраните изменения")

def show_api_setup():
    """Показывает инструкции по включению Google Drive API"""
    print("\n" + "="*60)
    print("📚 ВКЛЮЧЕНИЕ GOOGLE DRIVE API")
    print("="*60)
    
    print("\n1. 📋 Перейдите в Library:")
    print("   APIs & Services → Library")
    
    print("\n2. 🔍 Найдите 'Google Drive API'")
    
    print("\n3. ✅ Нажмите 'Enable'")
    
    print("\n4. ⏱️ Подождите активации API")

def create_web_credentials():
    """Создает credentials для Web application"""
    print("\n" + "="*60)
    print("🌐 СОЗДАНИЕ WEB APPLICATION CREDENTIALS")
    print("="*60)
    
    print("\n1. 📋 Создайте новые OAuth 2.0 Client ID:")
    print("   + CREATE CREDENTIALS → OAuth client ID")
    
    print("\n2. 🎯 Application type: Web application")
    
    print("\n3. 📝 Name: AI Mockup Generator Web")
    
    print("\n4. 🌐 Authorized redirect URIs:")
    print("   - http://localhost:8080")
    
    print("\n5. 💾 Создайте и скачайте JSON файл")
    
    print("\n6. 📁 Замените credentials.json новым файлом")

def main():
    """Основная функция"""
    print("🚀 Настройка Google Drive API для AI Mockup Generator")
    print("="*60)
    
    # Проверяем credentials
    creds_type = check_credentials_file()
    
    if not creds_type:
        print("\n❌ Не удалось определить тип credentials")
        print("📝 Следуйте инструкциям ниже для создания credentials")
        show_google_cloud_setup()
        return
    
    # Показываем соответствующие инструкции
    if creds_type == 'desktop':
        print("\n✅ Desktop Application credentials найдены")
        show_google_cloud_setup()
    elif creds_type == 'web':
        print("\n✅ Web Application credentials найдены")
        print("🌐 Для Web application добавьте redirect URI:")
        print("   http://localhost:8080")
    
    # Общие инструкции
    show_oauth_consent_setup()
    show_api_setup()
    
    print("\n" + "="*60)
    print("🎯 СЛЕДУЮЩИЕ ШАГИ")
    print("="*60)
    
    print("\n1. ✅ Выполните все настройки в Google Cloud Console")
    print("2. ⏱️ Подождите 2-3 минуты")
    print("3. 🧪 Запустите тест:")
    print("   python test_google_drive.py")
    
    print("\n💡 Если ошибка повторяется:")
    print("   - Проверьте, что все настройки сохранены")
    print("   - Попробуйте создать новые credentials")
    print("   - Очистите кэш браузера")
    
    # Предлагаем открыть Google Cloud Console
    try:
        response = input("\n🌐 Открыть Google Cloud Console? (y/n): ").strip().lower()
        if response in ['y', 'yes', 'да', 'д']:
            webbrowser.open('https://console.cloud.google.com/apis/credentials?project=quickstart-1591698112539')
            print("✅ Google Cloud Console открыт в браузере")
    except KeyboardInterrupt:
        print("\n👋 Настройка завершена")

if __name__ == "__main__":
    main()
