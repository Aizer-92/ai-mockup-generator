#!/usr/bin/env python3
"""
Проверка доступных папок на FTP сервере
"""

import ftplib
import os
from dotenv import load_dotenv

# Загружаем конфигурацию
load_dotenv('ftp_config.env')

def check_ftp_folders():
    """Проверяет доступные папки на FTP сервере"""
    print("🔍 Проверка папок на FTP сервере...")
    
    try:
        # Подключаемся к FTP
        ftp = ftplib.FTP()
        ftp.connect(os.getenv('FTP_HOST'), 21)
        ftp.login(os.getenv('FTP_USERNAME'), os.getenv('FTP_PASSWORD'))
        print("✅ FTP подключение успешно")
        
        # Получаем список папок
        print("\n📁 Содержимое корневой папки:")
        folders = []
        ftp.retrlines('LIST', folders.append)
        
        for folder in folders:
            print(f"  {folder}")
        
        # Пробуем перейти в разные папки
        test_folders = ['/var/www/html', '/var/www', '/www', '/public_html', '/htdocs']
        
        print("\n🔍 Проверка доступных папок:")
        for folder in test_folders:
            try:
                ftp.cwd(folder)
                print(f"✅ Доступна: {folder}")
                
                # Показываем содержимое
                contents = []
                ftp.retrlines('LIST', contents.append)
                print(f"   Содержимое: {len(contents)} элементов")
                
                # Возвращаемся в корень
                ftp.cwd('/')
                
            except Exception as e:
                print(f"❌ Недоступна: {folder} - {e}")
        
        ftp.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка FTP: {e}")
        return False

if __name__ == "__main__":
    check_ftp_folders()
