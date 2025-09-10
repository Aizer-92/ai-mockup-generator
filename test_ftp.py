#!/usr/bin/env python3
"""
Тест FTP подключения к серверу
"""
import sys
from ftp_uploader import FTPUploader

def test_ftp_connection():
    """Тестирует FTP подключение"""
    print("🔍 Тестирование FTP подключения...")
    
    # Получаем FTP загрузчик из конфигурации
    from ftp_uploader import get_ftp_uploader
    uploader = get_ftp_uploader()
    
    if not uploader:
        print("❌ Не удалось создать FTP загрузчик")
        print("📝 Проверьте настройки FTP в .env файле")
        return False
    
    # Тестируем подключение
    if uploader.test_connection():
        print("✅ FTP подключение успешно!")
        
        # Создаем папку
        if uploader.create_remote_directory():
            print("✅ Папка /mockups создана/найдена")
        else:
            print("❌ Ошибка создания папки")
            return False
        
        # Получаем список файлов
        files = uploader.list_files()
        print(f"📁 Найдено файлов в папке: {len(files)}")
        
        for file in files[:5]:  # Показываем первые 5 файлов
            print(f"   - {file.get('filename', 'Unknown')}")
        
        print("\n🎉 FTP настройка готова!")
        print("✅ Можете запускать: streamlit run main.py")
        return True
    else:
        print("❌ Ошибка FTP подключения")
        print("📝 Проверьте данные подключения в SERVER_FTP_SETUP.md")
        return False

if __name__ == "__main__":
    print("🚀 Тест FTP подключения к search.headcorn.pro")
    print("=" * 50)
    
    success = test_ftp_connection()
    
    if success:
        print("\n✅ Все готово! FTP работает корректно")
        sys.exit(0)
    else:
        print("\n❌ Нужна настройка FTP")
        print("📝 Следуйте инструкции в SERVER_FTP_SETUP.md")
        sys.exit(1)
