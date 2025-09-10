#!/usr/bin/env python3
"""
Очистка старых файлов с FTP сервера
"""

import ftplib
import os
from dotenv import load_dotenv

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def clean_ftp_files():
    """Удаляет все файлы из папки mockups на FTP сервере"""
    print("🧹 Очистка старых файлов с FTP сервера")
    print("=====================================")
    
    try:
        # Подключаемся к FTP
        ftp = ftplib.FTP()
        ftp.connect(os.getenv('FTP_HOST'), 21)
        ftp.login(os.getenv('FTP_USERNAME'), os.getenv('FTP_PASSWORD'))
        print("✅ FTP подключение успешно")
        
        # Переходим в папку mockups
        ftp.cwd('/public_html/mockups')
        print("✅ Перешли в папку mockups")
        
        # Получаем список файлов
        files = []
        ftp.retrlines('LIST', files.append)
        
        print(f"\n📁 Найдено файлов: {len(files)}")
        
        # Удаляем все файлы
        deleted_count = 0
        for file_info in files:
            parts = file_info.split()
            if len(parts) >= 9:
                filename = parts[-1]
                try:
                    ftp.delete(filename)
                    print(f"✅ Удален: {filename}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Ошибка удаления {filename}: {e}")
        
        print(f"\n🎉 Удалено файлов: {deleted_count}")
        
        # Проверяем, что папка пуста
        files_after = []
        ftp.retrlines('LIST', files_after.append)
        print(f"📁 Осталось файлов: {len(files_after)}")
        
        if len(files_after) == 0:
            print("✅ Папка полностью очищена")
        else:
            print("⚠️ В папке остались файлы:")
            for file_info in files_after:
                print(f"  {file_info}")
        
        ftp.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    clean_ftp_files()
