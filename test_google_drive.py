#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции с Google Drive
"""
import os
import sys
from google_drive_client import GoogleDriveClient

def test_google_drive_integration():
    """Тестирует интеграцию с Google Drive"""
    print("🔍 Тестирование интеграции с Google Drive...")
    
    # Проверяем наличие файла credentials.json
    if not os.path.exists('credentials.json'):
        print("❌ Файл credentials.json не найден!")
        print("📝 Создайте файл credentials.json с учетными данными OAuth")
        return False
    
    print("✅ Файл credentials.json найден")
    
    # Создаем клиент Google Drive
    try:
        client = GoogleDriveClient()
        print("✅ GoogleDriveClient создан успешно")
    except Exception as e:
        print(f"❌ Ошибка создания GoogleDriveClient: {e}")
        return False
    
    # Тестируем аутентификацию
    print("\n🔐 Тестирование аутентификации...")
    try:
        if client.authenticate():
            print("✅ Аутентификация успешна!")
        else:
            print("❌ Ошибка аутентификации")
            return False
    except Exception as e:
        print(f"❌ Ошибка аутентификации: {e}")
        return False
    
    # Тестируем создание папки
    print("\n📁 Тестирование создания папки...")
    try:
        folder_id = client.create_mockups_folder("AI Mockup Generator Test")
        if folder_id:
            print(f"✅ Папка создана/найдена: {folder_id}")
        else:
            print("❌ Ошибка создания папки")
            return False
    except Exception as e:
        print(f"❌ Ошибка создания папки: {e}")
        return False
    
    # Тестируем получение информации о диске
    print("\n💾 Тестирование получения информации о диске...")
    try:
        drive_info = client.get_drive_info()
        if drive_info:
            print("✅ Информация о диске получена:")
            print(f"   👤 Пользователь: {drive_info.get('user', 'Unknown')}")
            print(f"   📧 Email: {drive_info.get('email', 'Unknown')}")
            print(f"   💾 Использовано: {drive_info.get('storage_used', '0')} байт")
            print(f"   📁 ID папки: {drive_info.get('folder_id', 'Unknown')}")
        else:
            print("❌ Ошибка получения информации о диске")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения информации о диске: {e}")
        return False
    
    # Тестируем получение списка файлов
    print("\n📋 Тестирование получения списка файлов...")
    try:
        mockups = client.get_mockups_list(10)
        print(f"✅ Найдено мокапов: {len(mockups)}")
        for i, mockup in enumerate(mockups[:3]):  # Показываем первые 3
            print(f"   {i+1}. {mockup.get('filename', 'Unknown')} ({mockup.get('created_time', 'Unknown')})")
    except Exception as e:
        print(f"❌ Ошибка получения списка файлов: {e}")
        return False
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("✅ Google Drive интеграция работает корректно")
    return True

def test_upload_sample():
    """Тестирует загрузку тестового файла"""
    print("\n📤 Тестирование загрузки тестового файла...")
    
    try:
        client = GoogleDriveClient()
        if not client.authenticate():
            print("❌ Ошибка аутентификации")
            return False
        
        # Создаем тестовое изображение
        from PIL import Image
        import io
        
        # Создаем простое тестовое изображение
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Тестовые метаданные
        test_metadata = {
            "mockup_style": "Тестовый стиль",
            "logo_application": "Тестовое нанесение",
            "logo_placement": "Центр",
            "test": True
        }
        
        # Загружаем файл
        file_id = client.upload_mockup(
            img_bytes.getvalue(),
            "test_mockup.jpg",
            test_metadata
        )
        
        if file_id:
            print(f"✅ Тестовый файл загружен: {file_id}")
            
            # Скачиваем обратно для проверки
            downloaded_data = client.download_mockup(file_id)
            if downloaded_data:
                print("✅ Файл успешно скачан обратно")
                print(f"   Размер: {len(downloaded_data)} байт")
            else:
                print("❌ Ошибка скачивания файла")
            
            # Удаляем тестовый файл
            if client.delete_mockup(file_id):
                print("✅ Тестовый файл удален")
            else:
                print("❌ Ошибка удаления тестового файла")
            
            return True
        else:
            print("❌ Ошибка загрузки тестового файла")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования загрузки: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов Google Drive интеграции")
    print("=" * 50)
    
    # Основные тесты
    success = test_google_drive_integration()
    
    if success:
        # Тест загрузки
        upload_success = test_upload_sample()
        
        if upload_success:
            print("\n🎉 Все тесты пройдены успешно!")
            print("✅ Google Drive готов к использованию")
            sys.exit(0)
        else:
            print("\n⚠️ Основные тесты прошли, но есть проблемы с загрузкой")
            sys.exit(1)
    else:
        print("\n❌ Тесты не пройдены")
        print("📝 Проверьте настройки Google Drive API")
        sys.exit(1)
